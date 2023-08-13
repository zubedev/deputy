from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.urls import reverse

from config.mixins import TimeStampedStatusMixin
from core.managers import UserManager


class User(AbstractBaseUser, TimeStampedStatusMixin, PermissionsMixin):  # type: ignore
    """Default User model for deputy"""

    email = models.EmailField(
        "email address",
        unique=True,
        help_text="Email address of the user (required, max length = 254 chars).",
    )
    name = models.CharField(
        "name",
        max_length=254,
        help_text="Name of the user (required, max length = 254 chars).",
    )
    is_staff = models.BooleanField(
        "staff status",
        default=False,
        help_text="Designates whether the user can log into the admin site.",
    )

    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    class Meta:
        ordering = ["id"]
        verbose_name = "user"
        verbose_name_plural = "users"

    def __str__(self) -> str:
        return f"{self.name} <{self.email}>"

    def __repr__(self) -> str:
        return f"<User: id={self.id} name='{self.name}' email='{self.email}'>"

    def clean(self) -> None:
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_absolute_url(self) -> str:
        return reverse("user-detail", kwargs={"pk": self.pk})
