from django.urls import path

from apps.profile.presentation import views


app_name = "profile"

urlpatterns = [
    path("profile", views.profile, name="profile"),
]
