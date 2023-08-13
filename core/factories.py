from collections.abc import Sequence
from typing import Any

import factory
from django.contrib.auth import get_user_model
from factory import post_generation
from faker import Faker

faker = Faker()


class UserFactory(factory.django.DjangoModelFactory):  # type: ignore
    """Factory for User model"""

    class Meta:
        model = get_user_model()
        django_get_or_create = ["email"]

    name = factory.LazyAttribute(lambda x: faker.name())
    email = factory.LazyAttribute(lambda x: faker.email())
    is_staff = False
    is_superuser = False
    is_active = True

    @post_generation  # type: ignore
    def password(self, create: bool, extracted: Sequence[Any], **kwargs: Any) -> None:
        """Set password for User model"""
        password = extracted or faker.password()
        self.set_password(password)


class StaffuserFactory(UserFactory):
    """Factory for staff User model"""

    is_staff = True
    is_superuser = False


class SuperuserFactory(UserFactory):
    """Factory for super User model"""

    is_staff = True
    is_superuser = True
