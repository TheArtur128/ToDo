from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path("admin/", admin.site.urls),
    path('', include("apps.access.urls", namespace="access")),
    path('', include("apps.confirmation.urls", namespace="confirmation")),
    path('', include("apps.map.urls", namespace="map")),
    path('', include("apps.profile_.urls", namespace="profile_")),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATIC_ROOT
    )
