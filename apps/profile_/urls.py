from django.urls import path

from apps.profile_ import views


app_name = "profile_"

urlpatterns = [
    path("profile", views.profile, name="profile"),
]
