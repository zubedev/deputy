import json
from time import sleep
from typing import Any

import requests
from celery import chain, shared_task
from django.conf import settings
from scrapyd_client import ScrapydClient

from config.enums import ScrapyJobStatusEnums
from proxy.models import Proxy


@shared_task
def crawl_task(spider: str, spider_args: dict[str, Any] | None = None) -> dict[str, Any] | None:
    client = ScrapydClient(settings.SCRAPYD_URL)
    # schedule a scraping job and get its job id
    job_id = client.schedule(settings.SCRAPY_PROJECT, spider, spider_args or {})

    retries = 10
    while retries:  # get the list of jobs and check the status
        jobs: dict[str, list[dict[str, Any]]] = client.jobs(settings.SCRAPY_PROJECT)
        for status in ScrapyJobStatusEnums.values:
            for job in jobs[status]:
                if job["id"] == job_id and status == ScrapyJobStatusEnums.FINISHED.value:
                    return job
        retries -= 1
        sleep(5)  # wait 5 seconds then check again

    return None


@shared_task
def save_result_task(result: dict[str, Any] | None = None) -> list[dict[str, Any]] | None:
    # if the crawl task failed, result will be None
    if result is None:
        return None
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

    results = []  # response is a jsonlist, each line is a json object
    proxies = []  # proxies to be bulk created
    for line in response.text.splitlines():
        proxy = json.loads(line)
        results.append(proxy)
        proxies.append(
            Proxy(
                ip=proxy["ip"],
                port=proxy["port"],
                protocol=proxy["protocol"],
                country=proxy["country"],
                anonymity=proxy["anonymity"],
                source=proxy["source"],
            )
        )

    Proxy.objects.bulk_create(
        proxies,
        update_conflicts=True,
        update_fields=["country", "anonymity", "source"],
        unique_fields=["ip", "port", "protocol"],
    )
    return results


@shared_task(ignore_result=True)
def crawl_workflow() -> None:
    chain(crawl_task.s("proxynova"), save_result_task.s())()
