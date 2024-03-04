from django.urls import path

from apps.tasks.views import index


app_name = "tasks"

urlpatterns = [
    path('', index, name="map"),
]
