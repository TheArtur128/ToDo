from django.urls import path

from accounts.views import (
    login, registrate, logout, authorize, NameAccessRecovererView,
    EmailAccessRecovererView
)


app_name = 'accounts'

urlpatterns = [
    path('sign-in', login, name='sign-in'),
    path('sign-up', registrate, name='sign-up'),
    path('authorize/<str:token>', authorize, name='authorize'),
    path('logout', logout, name='logout'),
    path(
        'recover-access-by-name',
        NameAccessRecovererView.as_view(),
        name='recover-access-by-name',
    ),
    path(
        'recover-access-by-email',
        EmailAccessRecovererView.as_view(),
        name='recover-access-by-email',
    ),
]
