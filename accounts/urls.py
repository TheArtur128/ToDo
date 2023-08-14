from django.urls import path

from accounts.views import login


app_name = 'accounts'

urlpatterns = [
    path('sign-in', login, name='sign-in'),
]
