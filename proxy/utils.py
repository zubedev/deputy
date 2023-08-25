import logging
import random
from collections.abc import Sequence
from typing import Any

import requests
from django_countries import countries

from config.enums import ProtocolEnums
from config.lists import USER_AGENTS, WEBSITES
from proxy.types import CheckedProxyTypedDict, ProxyTypedDict

logger = logging.getLogger(__name__)


def check_proxy(ip: str, port: int | str, protocol: str = ProtocolEnums.HTTP.value) -> bool:
    """Returns True if the proxy is working, False otherwise."""
    logger.debug(f"Checking proxy {protocol}://{ip}:{port} ...")

    protocol = protocol.lower() if "socks" in protocol.lower() else "http"
    proxy = f"{protocol}://{ip}:{port}"
    proxies = {"http": proxy, "https": proxy}
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    url = random.choice(WEBSITES)

    logger.debug(f"Sending request to {url=} via {proxies=} ...")
    try:
        response = requests.get(url=url, headers=headers, proxies=proxies, timeout=10, allow_redirects=True)
        return response.ok
    except Exception as e:
        logger.debug(e)
    return False


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
