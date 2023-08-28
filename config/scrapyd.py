from scrapyd_client import ScrapydClient

from config import settings

client = ScrapydClient(url=settings.SCRAPYD_URL, username=settings.SCRAPYD_USERNAME, password=settings.SCRAPYD_PASSWORD)
