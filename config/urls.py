from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
]

if settings.DEBUG:  # expose schema views only in debug mode
    urlpatterns.extend(
        [
            path("schema/", SpectacularAPIView.as_view(), name="schema"),  # type: ignore
            path("schema/swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger"),  # type: ignore
            path("schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),  # type: ignore
        ]
    )
