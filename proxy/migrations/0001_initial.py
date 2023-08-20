import django_countries.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Proxy",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text="Date time on which the object was created.",
                        verbose_name="created at",
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True,
                        help_text="Date time on which the object was last updated.",
                        verbose_name="updated at",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True, help_text="Active status of the object.", verbose_name="active status"
                    ),
                ),
                (
                    "ip",
                    models.GenericIPAddressField(
                        help_text="ip address of the proxy (255.255.255.255).", verbose_name="ip address"
                    ),
                ),
                ("port", models.PositiveIntegerField(help_text="port of the proxy (1-65535).", verbose_name="port")),
                (
                    "protocol",
                    models.CharField(
                        choices=[("http", "Http"), ("https", "Https"), ("socks4", "Socks4"), ("socks5", "Socks5")],
                        default="http",
                        help_text="protocol of the proxy (http(s) or socks(4|5)).",
                        max_length=6,
                        verbose_name="protocol",
                    ),
                ),
                (
                    "country",
                    django_countries.fields.CountryField(default="", help_text="country of the proxy.", max_length=2),
                ),
                (
                    "anonymity",
                    models.CharField(
                        choices=[
                            ("unknown", "Unknown"),
                            ("transparent", "Transparent"),
                            ("anonymous", "Anonymous"),
                            ("elite", "Elite"),
                        ],
                        default="unknown",
                        help_text="anonymity of the proxy (unknown, transparent, anonymous, or elite).",
                        max_length=11,
                        verbose_name="anonymity",
                    ),
                ),
                ("source", models.SlugField(help_text="source of the proxy.", max_length=254, verbose_name="source")),
                (
                    "last_checked_at",
                    models.DateTimeField(
                        help_text="last time the proxy was checked.", null=True, verbose_name="last checked at"
                    ),
                ),
                (
                    "last_worked_at",
                    models.DateTimeField(
                        help_text="last time the proxy was checked and working.",
                        null=True,
                        verbose_name="last worked at",
                    ),
                ),
            ],
            options={
                "verbose_name": "proxy",
                "verbose_name_plural": "proxies",
                "ordering": ["-id"],
                "indexes": [models.Index(fields=["ip", "port"], name="index_proxy")],
            },
        ),
        migrations.AddConstraint(
            model_name="proxy",
            constraint=models.UniqueConstraint(fields=("ip", "port"), name="unique_proxy"),
        ),
    ]
