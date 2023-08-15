from itemadapter import ItemAdapter
from scrapy import Spider

from proxy.models import Proxy
from scraper.items import ProxyItem


class ProxyPipeline:
    async def add_to_db(self, item: ItemAdapter) -> None:
        await Proxy.objects.aupdate_or_create(
            ip=item["ip"],
            port=item["port"],
            protocol=item["protocol"],
            defaults={
                "anonymity": item["anonymity"],
                "country": item["country"],
                "source": item["source"],
            },
        )

    async def process_item(self, item: ProxyItem, spider: Spider) -> ProxyItem:
        adapter = ItemAdapter(item)
        await self.add_to_db(adapter)
        return item
