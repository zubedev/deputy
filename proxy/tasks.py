import json
from datetime import timedelta
from typing import Any

import requests
from celery import chain, chord, group, shared_task
from django.conf import settings
from django.db.models import QuerySet
from django.utils import timezone

from config.enums import ScrapyJobStatusEnums
from config.scrapyd import client
from proxy.models import Proxy
from proxy.types import CheckedProxyTypedDict, JobsTypedDict, JobTypedDict, ProxyTypedDict
from proxy.utils import check_proxy, get_country_code, remove_duplicates


@shared_task
def crawl_task(spider: str, spider_args: dict[str, Any] | None = None) -> str:
    # schedule a scraping job and get its job id
    return client.schedule(settings.SCRAPY_PROJECT, spider, spider_args or {})  # type: ignore[no-any-return]


@shared_task(max_retries=60, time_limit=300)  # time limit is 5 minutes
def get_crawl_result_task(job_id: str) -> list[ProxyTypedDict] | None:
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

    auth = None  # scrapyd basic auth
    if settings.SCRAPYD_USERNAME:
        auth = (settings.SCRAPYD_USERNAME, settings.SCRAPYD_PASSWORD)

    # download the jsonlist and save it to the database
    response = requests.get(url, auth=auth, allow_redirects=True)
    if not response.ok:
        return None

    # response is a jsonlist, each line is a json object
    return [json.loads(line) for line in response.text.splitlines()]


@shared_task
def check_proxies_task(proxy: ProxyTypedDict | CheckedProxyTypedDict | None) -> CheckedProxyTypedDict | None:
    if proxy is None:
        return None

    if not all([proxy.get("ip"), proxy.get("port")]):
        return None

    if "check_fail_count" not in proxy:
        proxy["check_fail_count"] = 0  # type: ignore[typeddict-unknown-key]
    if "last_checked_at" not in proxy:
        proxy["last_checked_at"] = None  # type: ignore[typeddict-unknown-key]
    if "last_worked_at" not in proxy:
        proxy["last_worked_at"] = None  # type: ignore[typeddict-unknown-key]
    proxy["is_active"] = False  # type: ignore[typeddict-unknown-key]

    result = CheckedProxyTypedDict(**proxy)  # type: ignore[misc]

    timestamp = timezone.now()

    checked_proxy = check_proxy(ip=proxy["ip"], port=proxy["port"])

    if checked_proxy["is_working"]:
        if not result.get("protocol"):
            result["protocol"] = checked_proxy["protocol"]
        elif "http" in result["protocol"] and "socks" in checked_proxy["protocol"]:
            result["protocol"] = checked_proxy["protocol"]
        elif "socks" in result["protocol"] and "http" in checked_proxy["protocol"]:
            result["protocol"] = checked_proxy["protocol"]

        if not result.get("country") and checked_proxy["country"]:
            result["country"] = checked_proxy["country"]
        elif result["country"] != checked_proxy["country"] and checked_proxy["country"]:
            result["country"] = checked_proxy["country"]

        result["anonymity"] = checked_proxy["anonymity"]
        result.update({"is_active": True, "last_worked_at": timestamp, "check_fail_count": 0})

    else:  # increment the fail count
        result["check_fail_count"] += 1

    result["last_checked_at"] = timestamp
    return result  # type: ignore[no-any-return]


@shared_task
def save_proxies_task(
    results: list[CheckedProxyTypedDict] | None,
    do_create: bool = True,
) -> list[CheckedProxyTypedDict] | None:
    # if the crawl task failed, result will be None
    if results is None:
        return None

    unique_fields = ["ip", "port"]
    update_fields = ["protocol", "check_fail_count", "last_checked_at", "last_worked_at", "is_active"]
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
    """Deletes dead proxies, where proxies that have not been working after 3 checks."""
    Proxy.objects.filter(check_fail_count__gte=3).delete()


@shared_task(ignore_result=True)
def recheck_workflow(slicing: int = 10) -> None:
    """Workflow for rechecking proxies that was checked more than an hour ago.
    chord:
    1. Get all proxies, for each, check_proxies_task(proxy) -> proxy (dict)
    2. Update the proxies, update_proxies_task(list[proxy]) -> results (list[proxy])
    """
    one_hour_ago = timezone.now() - timedelta(hours=1)

    qs: QuerySet[Proxy] = Proxy.objects.filter(last_checked_at__isnull=True)
    qs = qs | Proxy.objects.filter(last_checked_at__lte=one_hour_ago)
    proxies = qs.values("ip", "port", "protocol", "check_fail_count", "last_checked_at", "last_worked_at", "is_active")

    if not proxies.exists():
        return None

    for i in range(0, proxies.count(), slicing):
        chord([check_proxies_task.s(p) for p in proxies[i : i + slicing]])(save_proxies_task.s(do_create=False))


@shared_task(ignore_result=True)
def proxy_workflow(results: list[ProxyTypedDict] | None, slicing: int = 10) -> None:
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
    spiders = client.spiders(settings.SCRAPY_PROJECT)

    group([chain(crawl_task.s(s), get_crawl_result_task.s(), proxy_workflow.s()) for s in spiders])()
