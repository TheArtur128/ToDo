from django.urls import path

from access.views import (
    login, registrate, logout, authorize, AccessRecoveryByNameView,
    AccessRecoveryByEmailView
)


app_name = 'access'

urlpatterns = [
    path('sign-in', login, name='sign-in'),
    path('sign-up', registrate, name='sign-up'),
    path('authorize/<str:token>', authorize, name='authorize'),
    path('logout', logout, name='logout'),
    path(
        'recover-access-by-name',
        AccessRecoveryByNameView.as_view(),
        name='recover-access-by-name',
    ),
    path(
        'recover-access-by-email',
        AccessRecoveryByEmailView.as_view(),
        name='recover-access-by-email',
    ),
]
