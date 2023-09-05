from django_countries.serializers import CountryFieldMixin
from rest_framework import serializers

from proxy.models import Proxy


class ProxySerializer(CountryFieldMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Proxy
        fields = (
            "id",
            "ip",
            "port",
            "protocol",
            "country",
            "anonymity",
            "check_fail_count",
            "last_checked_at",
            "last_worked_at",
            "created_at",
            "updated_at",
            "is_active",
            "url",
        )
        read_only_fields = (
            "is_active",
            "check_fail_count",
            "last_checked_at",
            "last_worked_at",
            "created_at",
            "updated_at",
        )


class ProxyRandomSerializer(CountryFieldMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Proxy
        fields = ("ip", "port", "protocol", "country", "anonymity")
        read_only_fields = ("ip", "port", "protocol", "country", "anonymity")
