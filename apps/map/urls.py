from django.urls import path

from apps.map.views import map_


app_name = "map"

urlpatterns = [
    path('', map_, name="map"),
]
