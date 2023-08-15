from time import sleep
from typing import Any

from celery import shared_task
from scrapyd_client import ScrapydClient


@shared_task  # type: ignore
def crawl() -> dict[str, Any]:
    client = ScrapydClient("http://deputy-scrapyd:6800")
    # schedule a scraping job and get its job id
    job_id = client.schedule("scraper", "proxynova")

    retries = 10
    while retries:  # get the list of jobs and check the status
        jobs: dict[str, list[dict[str, Any]]] = client.jobs("scraper")
        for status in ["pending", "running", "finished"]:
            for job in jobs[status]:
                if job["id"] == job_id and status == "finished":
                    return job
        retries -= 1
        sleep(5)  # wait 5 seconds then check again
