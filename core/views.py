from collections.abc import Sequence
from typing import Any

from django.http import HttpResponsePermanentRedirect
from django.shortcuts import redirect
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request

from config.permissions import IsAdminOrSelf
from core.models import User
from core.serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):  # type: ignore
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

    def get_permissions(self) -> Sequence[Any]:
        """Return permissions based on action"""
        if self.action in ["me", "retrieve", "update", "partial_update", "destroy"]:
            return [IsAdminOrSelf()]
        return super().get_permissions()

    @action(detail=False, methods=["get"])
    def me(self, request: Request) -> HttpResponsePermanentRedirect:
        """/users/me/ -> /users/{pk}/"""
        return redirect(request.user.get_absolute_url())  # type: ignore
