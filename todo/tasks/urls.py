from django.urls import path 

from tasks.views import login


app_name = 'tasks'

urlpatterns = [
    path('login', login, name='login')
]