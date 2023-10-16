from django.urls import path

from apps.access.views import (
    login, registrate, logout, access_recovery_by_name, access_recovery_by_email
)


app_name = "access"

urlpatterns = [
    path("sign-in", login, name="sign-in"),
    path("sign-up", registrate, name="sign-up"),
    path("logout", logout, name="logout"),
    path(
        "recover-access-by-name",
        access_recovery_by_name,
        name="recover-access-by-name"
    ),
    path(
        "recover-access-by-email",
        access_recovery_by_email,
        name="recover-access-by-email"
    ),
]
