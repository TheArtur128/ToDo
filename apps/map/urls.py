from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.map import views


router = DefaultRouter()

router.register("tasks", views.TaskViewSet, "task")

app_name = "map"

urlpatterns = [
    path('', views.map_, name="map"),
    path('api/0.1v/map/', include(router.urls)),
    path(
        'api/0.1v/map/top-map-tasks',
        views.TopMapTaskViewSet.as_view({'post': 'create'}),
        name="top-map-tasks",
    ),
    path(
        'api/0.1v/map/top-map-tasks/<int:id>',
        views.TopMapTaskViewSet.as_view({'get': 'list'}),
        name="top-map-tasks",
    ),
]
