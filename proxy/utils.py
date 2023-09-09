import logging
import time
from collections.abc import Sequence
from typing import Any

from django_countries import countries

from config.inspector import inspector
from proxy.types import CheckedProxyTypedDict, CheckProxyResultTypedDict, ProxyTypedDict

logger = logging.getLogger(__name__)


def check_proxy(ip: str, port: int | str) -> CheckProxyResultTypedDict:
    """Returns True if the proxy is working, False otherwise."""
    logger.debug(f"Checking proxy {ip}:{port} ...")

    result = CheckProxyResultTypedDict(
        ip=ip,
        port=int(port),
        protocol="",
        country="",
        anonymity="transparent",
        speed=0,
        is_working=False,
    )
    protocols = ["http", "socks4", "socks5"]

    for protocol in protocols:
        proxy = f"{protocol}://{ip}:{port}"
        logger.debug(f"Sending request to inspector via {proxy=} ...")
        proxies = {"http": proxy, "https": proxy}

        start_time = time.perf_counter_ns()
        response = inspector.get_headers(proxies=proxies)
        elapsed_time = int((time.perf_counter_ns() - start_time) / 1000000)  # in milliseconds

        if not response:
            continue

        # at this point, the proxy is working, set the values and break
        result["protocol"] = protocol
        result["country"] = response["country"]
        result["speed"] = elapsed_time

        if response["ip"] == ip:
            headers = ["via", "from", "x_real_ip", "client_ip", "x_proxy_id", "proxy_authorization", "proxy_connection"]
            if any(header in response for header in headers):
                result["anonymity"] = "anonymous"
            else:
                result["anonymity"] = "elite"

        result["is_working"] = True
        break

    return result


def remove_duplicates(
    items: Sequence[dict[str, Any] | ProxyTypedDict | CheckedProxyTypedDict],
    unique_keys: Sequence[str],
) -> Sequence[dict[str, Any] | ProxyTypedDict | CheckedProxyTypedDict]:
    """Removes duplicate items from the given list of dicts based on the given unique keys."""
    seen = set()
    unique_items = []
    for item in items:
        if not item:
            continue
        unique_values = tuple(item.get(key) for key in unique_keys)
        if unique_values not in seen:
            seen.add(unique_values)
            unique_items.append(item)
    return unique_items


def get_country_code(name: str, regex: bool = False) -> str:
    """Returns the country code for the given country name if found, empty string otherwise.

    WARNING: This function is not reliable, it returns the first country code matched.
    """
    if not name:
        return ""

    # sites where they have partial names and `countries` can't lookup properly below
    if name.lower() in ["america", "united states", "usa"]:
        return "US"

    c = countries.by_name(name, regex=regex)  # type: ignore[call-overload]

    if not c:
        return ""

    if isinstance(c, str):  # when regex=False, c is a str
        return c
    elif isinstance(c, list | tuple | set):
        # WARNING: highly unreliable - returns the first country code matched
        return c[0]  # type: ignore

    return ""
