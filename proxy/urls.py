from rest_framework import routers

from proxy.views import ProxyViewSet

router = routers.DefaultRouter()
router.register(r"proxies", ProxyViewSet)

urlpatterns = router.urls
