from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path("admin/", admin.site.urls),
    path('', include("apps.access.presentation.urls", namespace="access")),
    path('', include("apps.confirmation.urls", namespace="confirmation")),
    path('', include("apps.profile.presentation.urls", namespace="profile")),
    path('', include("apps.tasks.presentation.urls", namespace="tasks")),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATIC_ROOT
    )
