from django.urls import path

from apps.access import views


app_name = "access"

urlpatterns = [
    path("sign-in", views.login, name="sign-in"),
    path("sign-up", views.registrate, name="sign-up"),
    path("logout", views.logout, name="logout"),
    path(
        "restore-access-by-name",
        views.restore_access_by_name,
        name="restore-by-name"
    ),
    path(
        "restore-access-by-email",
        views.restore_access_by_email,
        name="restore-by-email"
    ),
    path(
        "profile",
        views.profile,
        name="profile",
    ),
]
