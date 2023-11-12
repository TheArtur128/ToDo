from django.urls import path

from apps.access.views import (
    login, registrate, logout, restore_access_by_name, restore_access_by_email
)


app_name = "access"

urlpatterns = [
    path("sign-in", login, name="sign-in"),
    path("sign-up", registrate, name="sign-up"),
    path("logout", logout, name="logout"),
    path(
        "restore-access-by-name",
        restore_access_by_name,
        name="restore-by-name"
    ),
    path(
        "restore-access-by-email",
        restore_access_by_email,
        name="restore-by-email"
    ),
]
