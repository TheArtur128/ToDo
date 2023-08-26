from django.urls import path

from access.views import (
    login, registrate, logout, authorize, access_recovery_by_name,
    access_recovery_by_email)


app_name = "access"

urlpatterns = [
    path("sign-in", login, name="sign-in"),
    path("sign-up", registrate, name="sign-up"),
    path("authorize/<str:token>", authorize, name="authorize"),
    path("logout", logout, name="logout"),
    path(
        "recover-access-by-name",
        access_recovery_by_name,
        name="recover-access-by-name"),
    path(
        "recover-access-by-email",
        access_recovery_by_email,
        name="recover-access-by-email")]
