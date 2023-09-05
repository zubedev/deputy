import random
from collections.abc import Sequence

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, BasePermission, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer
from rest_framework.throttling import BaseThrottle, ScopedRateThrottle

from config.enums import AnonymityEnums, ProtocolEnums
from proxy.models import Proxy
from proxy.serializers import ProxyRandomSerializer, ProxySerializer


class ProxyViewSet(viewsets.ModelViewSet):  # type: ignore
    queryset = Proxy.objects.all()
    serializer_class = ProxySerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["protocol", "country", "anonymity"]
    throttle_scope = "proxies_random"  # for use with ScopedRateThrottle for /proxies/random/ endpoint

    def get_permissions(self) -> Sequence[IsAuthenticated | AllowAny | BasePermission]:
        """Return permissions based on action"""
        if self.action in ["random"]:
            return [AllowAny()]
        return super().get_permissions()  # type: ignore[return-value]

    def get_throttles(self) -> list[ScopedRateThrottle | BaseThrottle]:
        """Return throttles based on action"""
        if self.action in ["random"]:
            return [ScopedRateThrottle()]
        return super().get_throttles()

    def get_serializer_class(self) -> type[ProxySerializer | ProxyRandomSerializer | BaseSerializer]:  # type: ignore
        """Return serializer class based on action"""
        if self.action in ["random"]:
            return ProxyRandomSerializer
        return super().get_serializer_class()

    @extend_schema(
        parameters=[
            OpenApiParameter("protocol", OpenApiTypes.STR, OpenApiParameter.QUERY, enum=ProtocolEnums.values),
            OpenApiParameter("country", OpenApiTypes.STR, OpenApiParameter.QUERY, pattern=r"^[A-Z]{2}$"),
            OpenApiParameter("anonymity", OpenApiTypes.STR, OpenApiParameter.QUERY, enum=AnonymityEnums.values),
        ]
    )
    @action(detail=False, methods=["get"])
    def random(self, request: Request) -> Response:
        """/proxies/random/"""
        qs = self.filter_queryset(self.get_queryset().filter(is_active=True))
        if not qs.exists():
            return Response({"message": "No active proxies found."})

        pk_list = qs.values_list("pk", flat=True)
        pk_random = random.choice(pk_list)
        proxy = qs.values("ip", "port", "protocol", "country", "anonymity").get(pk=pk_random)

        serializer = self.get_serializer(proxy)
        return Response(serializer.data)
