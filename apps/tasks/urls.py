from django.urls import path

from apps.tasks.presentation.views import index


app_name = "tasks"

urlpatterns = [
    path('', index, name="index"),
]
