from django.urls import path

from access.views import login


app_name = 'access'

urlpatterns = [
    path('login', login, name='login')
]
