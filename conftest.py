from typing import TYPE_CHECKING

import pytest
from pytest_factoryboy import register
from rest_framework.test import APIClient

from core import factories

if TYPE_CHECKING:
    from core.models import User

register(factories.UserFactory, "user")
register(factories.StaffuserFactory, "staffuser")
register(factories.SuperuserFactory, "superuser")


@pytest.fixture()
@pytest.mark.django_db()
def admin_user(django_user_model: "User") -> "User":
    """Overriding the default admin user fixture to also pass the `name` field"""
    user_data = {"name": "Admin", "email": "admin@test.local", "password": "Pass123#"}
    return django_user_model.objects.create_superuser(**user_data)


@pytest.fixture()
def api_client() -> APIClient:
    """A Django Rest Framework test client instance"""
    return APIClient()
