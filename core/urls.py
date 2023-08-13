from rest_framework import routers

from core.views import UserViewSet

router = routers.DefaultRouter()
router.register(r"users", UserViewSet)

urlpatterns = router.urls
