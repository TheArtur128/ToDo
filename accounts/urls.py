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
]
