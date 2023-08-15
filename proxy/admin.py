from django.contrib import admin

from proxy.models import Proxy


@admin.register(Proxy)
class ProxyAdmin(admin.ModelAdmin[Proxy]):
    date_hierarchy = "created_at"
    list_display = (
        "__str__",
        "country",
        "anonymity",
        "source",
        "is_active",
        "last_checked_at",
        "created_at",
        "updated_at",
    )
    list_filter = ("protocol", "anonymity", "is_active", "source", "country")
    ordering = ("-id",)
    search_fields = ("id", "ip", "port", "source", "country")
    readonly_fields = ("url", "is_stale", "created_at", "updated_at", "last_checked_at")
