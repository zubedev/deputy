import sys
from importlib import import_module, reload
from types import ModuleType

import pytest
from django.conf import LazySettings
from django.urls import clear_url_caches
from rest_framework.test import APIClient


class TestUrls:
    def reload_urlconf(self, settings: LazySettings) -> ModuleType:
        if settings.ROOT_URLCONF in sys.modules:
            reload(sys.modules[settings.ROOT_URLCONF])
        return import_module(settings.ROOT_URLCONF)

    @pytest.mark.django_db()
    def test_schema_visibility(self, api_client: APIClient, settings: LazySettings) -> None:
        settings.DEBUG = True
        clear_url_caches()
        self.reload_urlconf(settings)

        res1 = api_client.get("/schema/")
        assert res1.status_code == 200

        res2 = api_client.get("/schema/swagger/")
        assert res2.status_code == 200

        res3 = api_client.get("/schema/redoc/")
        assert res3.status_code == 200

        settings.DEBUG = False
        clear_url_caches()
        self.reload_urlconf(settings)

        res4 = api_client.get("/schema/")
        assert res4.status_code == 404

        res5 = api_client.get("/schema/swagger/")
        assert res5.status_code == 404

        res6 = api_client.get("/schema/redoc/")
        assert res6.status_code == 404
