from django.shortcuts import render
from django.contrib import auth

from tasks.forms import UserLoginForm


def login(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)

        if form.is_valid():
            user = auth.authenticate(
                request,
                username=request.POST['username'],
                password=request.POST['password'],
            )

            if user:
                auth.login(request, user)

    else:
        form = UserLoginForm()

    return render(request, 'login.html', dict(form=form))
