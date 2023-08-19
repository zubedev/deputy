from time import sleep
from typing import Any

from celery import shared_task
from django.conf import settings
from scrapyd_client import ScrapydClient

from config.enums import ScrapyJobStatusEnums


@shared_task  # type: ignore
def crawl() -> dict[str, Any]:
    client = ScrapydClient(settings.SCRAPYD_URL)
    # schedule a scraping job and get its job id
    job_id = client.schedule(settings.SCRAPY_PROJECT, "proxynova")

    retries = 10
    while retries:  # get the list of jobs and check the status
        jobs: dict[str, list[dict[str, Any]]] = client.jobs(settings.SCRAPY_PROJECT)
        for status in ScrapyJobStatusEnums.values:
            for job in jobs[status]:
                if job["id"] == job_id and status == ScrapyJobStatusEnums.FINISHED.value:
                    return job
        retries -= 1
        sleep(5)  # wait 5 seconds then check again
