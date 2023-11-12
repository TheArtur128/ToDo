from django.urls import path

from apps.confirmation.views import confirm


app_name = "confirmation"

urlpatterns = [
    path(
        "confirm/<str:subject>/<str:method>/<str:session_token>",
        confirm,
        name="confirm"
    ),
]
