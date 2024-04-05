from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.map import views


router = DefaultRouter()

router.register("tasks", views.TaskViewSet, "task")
router.register("top-maps", views.TopMapViewSet, "top-map")

app_name = "map"

urlpatterns = [
    path('', views.map_selection_view, name="map-selection"),
    path('map/<int:top_map_id>', views.map_view, name="map"),
    path('api/0.1v/map/', include(router.urls)),
    path(
        'api/0.1v/map/top-maps/<int:top_map_id>/tasks/',
        views.TopMapTaskViewSet.as_view({'get': 'list', 'post': 'create'}),
        name="top-map-tasks",
    ),
]
