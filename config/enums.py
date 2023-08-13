from django.db.models import TextChoices


class ProtocolEnums(TextChoices):
    HTTP = "http"
    HTTPS = "https"
    SOCKS4 = "socks4"
    SOCKS5 = "socks5"


class AnonymityEnums(TextChoices):
    UNKNOWN = "unknown"
    TRANSPARENT = "transparent"
    ANONYMOUS = "anonymous"
    ELITE = "elite"
