from django.db import models
from django.utils import timezone

from config.enums import AnonymityEnums, ProtocolEnums
from config.mixins import BaseModel


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
    last_checked_at = models.DateTimeField(
        "last checked at",
        null=True,
        help_text="last time the proxy was checked.",
    )

    class Meta:
        verbose_name = "proxy"
        verbose_name_plural = "proxies"
        ordering = ["-id"]
        constraints = [models.UniqueConstraint(fields=["ip", "port", "protocol"], name="unique_proxy")]
        indexes = [models.Index(fields=["ip", "port", "protocol"], name="index_proxy")]

    @property
    def url(self) -> str:
        """Returns the proxy in the format of protocol://ip:port"""
        return f"{self.protocol}://{self.ip}:{self.port}"

    def __str__(self) -> str:
        """Returns the proxy in the format of protocol://ip:port"""
        return self.url

    def __repr__(self) -> str:
        """Returns the proxy in the format of <Proxy pk=1 data=protocol://ip:port>"""
        if self.pk:
            return f"<{self.__class__.__name__} pk={self.pk} data={self.url}>"
        return f"<{self.__class__.__name__} data={self.url}>"

    @property
    def is_stale(self) -> bool:
        """Returns True if the proxy is stale: last_checked_at is more than 1 hour ago"""
        if not self.last_checked_at:
            return True
        return (timezone.now() - self.last_checked_at).total_seconds() > 3600
