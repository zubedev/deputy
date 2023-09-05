from django.db import models
from django.urls import reverse
from django.utils import timezone
from django_countries.fields import CountryField

from config.enums import AnonymityEnums, ProtocolEnums
from config.mixins import BaseModel
from proxy.utils import check_proxy


class Proxy(BaseModel):
    """Proxy model"""

    ip = models.GenericIPAddressField(
        "ip address",
        help_text="ip address of the proxy (255.255.255.255).",
    )
    port = models.PositiveIntegerField(
        "port",
        help_text="port of the proxy (1-65535).",
    )
    protocol = models.CharField(
        "protocol",
        max_length=6,
        choices=ProtocolEnums.choices,
        default=ProtocolEnums.HTTP,
        help_text="protocol of the proxy (http(s) or socks(4|5)).",
    )
    country = CountryField(default="", help_text="country of the proxy.")
    anonymity = models.CharField(
        "anonymity",
        max_length=11,
        choices=AnonymityEnums.choices,
        default=AnonymityEnums.UNKNOWN,
        help_text="anonymity of the proxy (unknown, transparent, anonymous, or elite).",
    )
    source = models.SlugField(
        "source",
        max_length=254,
        help_text="source of the proxy.",
    )
    check_fail_count = models.PositiveIntegerField(
        "check fail count",
        default=0,
        help_text="number of times the proxy has been checked since it worked last.",
    )
    last_checked_at = models.DateTimeField(
        "last checked at",
        null=True,
        help_text="last time the proxy was checked.",
    )
    last_worked_at = models.DateTimeField(
        "last worked at",
        null=True,
        help_text="last time the proxy was checked and working.",
    )

    class Meta:
        verbose_name = "proxy"
        verbose_name_plural = "proxies"
        ordering = ["-id"]
        constraints = [models.UniqueConstraint(fields=["ip", "port"], name="unique_proxy")]
        indexes = [models.Index(fields=["ip", "port"], name="index_proxy")]

    def __str__(self) -> str:
        """Returns the proxy in the format of ip:port"""
        return f"{self.ip}:{self.port}"

    def __repr__(self) -> str:
        """Returns the proxy in the format of <Proxy pk=1 data=protocol://ip:port>"""
        if self.pk:
            return f"<{self.__class__.__name__} pk={self.pk} data={self.__str__()}>"
        return f"<{self.__class__.__name__} data={self.__str__()}>"

    def get_absolute_url(self) -> str:
        return reverse("proxy-detail", kwargs={"pk": self.pk})

    @property
    def url_format(self) -> str:
        """Returns the proxy in the format of protocol://ip:port"""
        return f"{self.protocol}://{self.ip}:{self.port}"

    @property
    def is_stale(self) -> bool:
        """Returns True if the proxy is stale: last_checked_at is more than 1 hour ago"""
        if not self.last_checked_at:
            return True
        return (timezone.now() - self.last_checked_at).total_seconds() > 3600  # 3600 seconds = 1 hour

    @property
    def is_working(self) -> bool:
        """Returns True if the proxy is working, False otherwise. Despite the is_active field."""
        return check_proxy(self.ip, self.port, self.protocol)

    @property
    def is_dead(self) -> bool:
        """Returns True if the proxy is dead, False otherwise."""
        return self.check_fail_count >= 3
