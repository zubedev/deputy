from scrapy.item import Field, Item


class ProxyItem(Item):  # type: ignore
    ip = Field()
    port = Field()
    protocol = Field()
    anonymity = Field()
    source = Field()
