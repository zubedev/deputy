import logging
from typing import Any, TypedDict

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class InspectorRootResponse(TypedDict):
    app_name: str
    app_description: str
    app_version: str


class InspectorHeadersResponse(TypedDict):
    ip: str
    host: str
    protocol: str
    country: str


class InspectorCountryResponse(TypedDict):
    ip: str
    country: str


class Inspector:
    """Inspector helper class for sending requests to INSPECTOR_URL."""

    def __init__(self, inspector_url: str = settings.INSPECTOR_URL, timeout: int = 10) -> None:
        self.inspector_url = inspector_url
        self.timeout = timeout

    def get_url(self, endpoint: str) -> str:
        return f"{self.inspector_url}/{endpoint}"

    def make_request(self, endpoint: str, proxies: dict[str, str] | None = None, **kwargs: Any) -> dict[str, Any]:
        try:
            response = requests.get(self.get_url(endpoint), proxies=proxies, timeout=self.timeout, **kwargs)
            response.raise_for_status()
        except Exception:
            return {}
        return response.json()  # type: ignore[no-any-return]

    def get_root(self, proxies: dict[str, str] | None = None, **kwargs: Any) -> InspectorRootResponse:
        response_body = self.make_request("", proxies=proxies, **kwargs)
        return InspectorRootResponse(**response_body)  # type: ignore

    def get_headers(self, proxies: dict[str, str] | None = None, **kwargs: Any) -> InspectorHeadersResponse:
        response_body = self.make_request("headers", proxies=proxies, **kwargs)
        return InspectorHeadersResponse(**response_body)  # type: ignore

    def get_country(self, proxies: dict[str, str] | None = None, **kwargs: Any) -> InspectorCountryResponse:
        response_body = self.make_request("country", proxies=proxies, **kwargs)
        return InspectorCountryResponse(**response_body)  # type: ignore


inspector = Inspector()
