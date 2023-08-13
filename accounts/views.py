from django.shortcuts import render, HttpResponseRedirect
from django.contrib import auth

from accounts.forms import UserLoginForm


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

                return HttpResponseRedirect('/')

    else:
        form = UserLoginForm()

    return render(request, 'login.html', dict(form=form))
