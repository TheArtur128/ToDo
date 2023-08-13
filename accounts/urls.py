from django.urls import path

from accounts.views import login


app_name = 'accounts'

urlpatterns = [
    path('login', login, name='login')
]
