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


class ScrapyJobStatusEnums(TextChoices):
    PENDING = "pending"
    RUNNING = "running"
    FINISHED = "finished"


class ProxyJudgeEnums(TextChoices):
    AZENV = "http://azenv.net"
    CLOUDFLARE = "https://www.cloudflare.com/cdn-cgi/trace"
    HTTPHEADER = "http://httpheader.net/azenv.php"
    PROXYSCRAPE = "https://proxyscrape.com/azenv"
