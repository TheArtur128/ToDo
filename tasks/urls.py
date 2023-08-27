from django.urls import path

from tasks.views import index


app_name = "tasks"

urlpatterns = [
    path('', index, name="index")
]
