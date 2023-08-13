from typing import TYPE_CHECKING

from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.views import APIView

if TYPE_CHECKING:
    from core.models import User


class IsAdminOrSelf(IsAuthenticated):
    def has_object_permission(self, request: Request, view: APIView, obj: "User") -> bool:
        return bool(request.user.is_staff) or request.user == obj
