import logging
import random

import requests

from config.enums import ProtocolEnums
from config.lists import USER_AGENTS, WEBSITES

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
