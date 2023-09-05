from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import RedirectView
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    # redirect root path to swagger schema view
    path("", RedirectView.as_view(pattern_name="swagger"), name="root"),
    path("admin/", admin.site.urls),
    # include app urls
    path("", include("core.urls")),
    path("", include("proxy.urls")),
    # drf-spectacular schema views
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("schema/swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger"),
    path("schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
