from django.urls import path

from apps.access.view import routes


app_name = "access"

urlpatterns = [
    path("sign-in", routes.login, name="sign-in"),
    path("sign-up", routes.registrate, name="sign-up"),
    path("logout", routes.logout, name="logout"),
    path(
        "restore-access-by-name",
        routes.restore_access_by_name,
        name="restore-by-name"
    ),
    path(
        "restore-access-by-email",
        routes.restore_access_by_email,
        name="restore-by-email"
    ),
    path(
        "profile",
        routes.profile,
        name="profile",
    ),
]
