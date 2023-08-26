import json
from datetime import timedelta
from typing import Any

import requests
from celery import chain, chord, group, shared_task
from django.conf import settings
from django.utils import timezone
from scrapyd_client import ScrapydClient

from config.enums import ProtocolEnums, ScrapyJobStatusEnums
from proxy.models import Proxy
from proxy.types import CheckedProxyTypedDict, JobsTypedDict, JobTypedDict, ProxyTypedDict
from proxy.utils import check_proxy, get_country_code, remove_duplicates


@shared_task
def crawl_task(spider: str, spider_args: dict[str, Any] | None = None) -> str:
    client = ScrapydClient(settings.SCRAPYD_URL)
    # schedule a scraping job and get its job id
    return client.schedule(settings.SCRAPY_PROJECT, spider, spider_args or {})  # type: ignore[no-any-return]


@shared_task(max_retries=60, time_limit=300)  # time limit is 5 minutes
def get_crawl_result_task(job_id: str) -> list[ProxyTypedDict] | None:
    client = ScrapydClient(settings.SCRAPYD_URL)
    result: JobTypedDict | None = None

    # get the list of jobs and check the status
    jobs: JobsTypedDict = client.jobs(settings.SCRAPY_PROJECT)
    for status in ScrapyJobStatusEnums.values:
        for job in jobs[status]:  # type: ignore[literal-required]
            if job["id"] == job_id and status == ScrapyJobStatusEnums.FINISHED.value:
                result = job
                break

    # keep retrying until the job is finished
    if result is None:
        raise get_crawl_result_task.retry(countdown=5)  # retry after 5 seconds

    # check for "items_url" in the job result
    if "items_url" not in result:
        return None

    # read the items url jsonlist from the job result
    items_url = result["items_url"]
    url = f"{settings.SCRAPYD_URL}{items_url}"

    # download the jsonlist and save it to the database
    response = requests.get(url, allow_redirects=True)
    if not response.ok:
        return None

    # response is a jsonlist, each line is a json object
    return [json.loads(line) for line in response.text.splitlines()]


@shared_task
def check_proxies_task(proxy: ProxyTypedDict | CheckedProxyTypedDict | None) -> CheckedProxyTypedDict | None:
    if proxy is None:
        return None

    if not all([proxy.get("ip", False), proxy.get("port", False)]):
        return None

    result: CheckedProxyTypedDict = {**proxy, "is_active": False}  # type: ignore[misc]
    timestamp = timezone.now()
    if check_proxy(
        ip=proxy["ip"],
        port=proxy["port"],
        protocol=proxy.get(  # type: ignore[arg-type]
            "protocol",
            ProtocolEnums.HTTP.value,
        ),
    ):
        result.update({"is_active": True, "last_worked_at": timestamp})

    result["last_checked_at"] = timestamp
    return result


@shared_task
def save_proxies_task(
    results: list[CheckedProxyTypedDict] | None,
    do_create: bool = True,
) -> list[CheckedProxyTypedDict] | None:
    # if the crawl task failed, result will be None
    if results is None:
        return None

    unique_fields = ["ip", "port"]
    update_fields = ["protocol", "last_checked_at", "last_worked_at", "is_active"]
    if do_create:  # add more fields to update for new proxies
        update_fields.extend(["country", "anonymity", "source"])
        # remove duplicates based on ip and port during creation
        results = remove_duplicates(results, unique_keys=unique_fields)  # type: ignore[assignment]

    proxies = []
    for proxy in results:
        # if the proxy didn't pass the check or missing ip/port, skip it
        if not proxy:
            continue
        # do some country validation
        country = proxy.get("country", "")
        if do_create and country and len(country) > 2:
            proxy["country"] = get_country_code(country)
        proxies.append(Proxy(**proxy))

    Proxy.objects.bulk_create(proxies, update_conflicts=True, update_fields=update_fields, unique_fields=unique_fields)
    return results


@shared_task
def dead_proxies_cleanup_task() -> None:
    """Deletes dead proxies, where proxies that have not been working for more than 1 day."""
    one_day_ago = timezone.now() - timedelta(days=1)
    # First, find proxies that are atleast 1 day old and not active
    queryset = Proxy.objects.filter(created_at__lt=one_day_ago, is_active=False)
    # Then, find proxies that have not been working for more than 1 day or never worked
    queryset = queryset.filter(last_worked_at__lt=one_day_ago) | queryset.filter(last_worked_at__isnull=True)
    # Finally, delete the proxies
    queryset.delete()


@shared_task(ignore_result=True)
def recheck_workflow(slicing: int = 100) -> None:
    """Workflow for rechecking proxies.
    chord:
    1. Get all proxies, for each, check_proxies_task(proxy) -> proxy (dict)
    2. Update the proxies, update_proxies_task(list[proxy]) -> results (list[proxy])
    """
    proxies = Proxy.objects.values("ip", "port", "protocol", "last_checked_at", "last_worked_at", "is_active")
    if not proxies.exists():
        return None

    for i in range(0, proxies.count(), slicing):
        chord([check_proxies_task.s(p) for p in proxies[i : i + slicing]])(save_proxies_task.s(do_create=False))


@shared_task(ignore_result=True)
def proxy_workflow(results: list[ProxyTypedDict] | None, slicing: int = 100) -> None:
    """Workflow for checking and saving proxies. This is continuation from crawl_workflow().

    chain: check crawl_workflow() for more details
    1. ...
    2. ...

    chord: this is continuation from crawl_workflow()
    3. Check the proxies, for each, check_proxies_task(proxy) -> proxy (dict)
    4. Save the proxies, save_proxies_task(list[proxy]) -> results (list[proxy])
    """
    if results is None:
        return None

    for i in range(0, len(results), slicing):
        chord([check_proxies_task.s(r) for r in results[i : i + slicing]])(save_proxies_task.s(do_create=True))


@shared_task(ignore_result=True)
def crawl_workflow() -> None:
    """Workflow for crawling proxies.

    group: run the spiders in parallel, and for each spider, run the following:

    chain:
    1. Crawl and scrape proxies within scrapyd, crawl_task() -> job_id
    2. Get the crawl result from scrapyd, get_crawl_result_task(job_id) -> results (jsonlist -> list[proxy])

    chord: continued in proxy_workflow()
    3. ...
    4. ...
    """
    client = ScrapydClient(settings.SCRAPYD_URL)
    spiders = client.spiders(settings.SCRAPY_PROJECT)

    group([chain(crawl_task.s(s), get_crawl_result_task.s(), proxy_workflow.s()) for s in spiders])()
