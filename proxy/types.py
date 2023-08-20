from datetime import datetime
from typing import TypedDict


class JobTypedDict(TypedDict):
    project: str
    spider: str
    id: str  # uuid
    start_time: str  # datetime
    end_time: str  # datetime
    log_url: str  # relative url .log extension
    items_url: str  # relative url .jl extension


class JobsTypedDict(TypedDict):
    node_name: str
    status: str
    pending: list[JobTypedDict]
    running: list[JobTypedDict]
    finished: list[JobTypedDict]


class ProxyTypedDict(TypedDict):
    ip: str  # 255.255.255.255
    port: int  # 1-65535
    protocol: str | None  # http, https, socks4, socks5 (optional)
    country: str | None  # country code (ISO 3166-1 alpha-2) (optional)
    anonymity: str | None  # transparent, anonymous, elite (optional)
    source: str | None  # scraped proxy site name or slug (optional)


class CheckedProxyTypedDict(ProxyTypedDict):
    # includes all fields from ProxyTypedDict
    is_active: bool
    last_checked_at: datetime | None  # datetime (optional)
    last_worked_at: datetime | None  # datetime (optional)
