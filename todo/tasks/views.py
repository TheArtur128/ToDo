from django.shortcuts import render, HttpResponse
from django.contrib.auth import authenticate, login

from tasks.forms import UserLoginForm


def login(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)

        if form.is_valid():
            user = authenticate(
                request,
                username=request.POST['username'],
                password=request.POST['password'],
            )

            if user:
                login(request, user)

    else:
        form = UserLoginForm()

    return render(request, 'login.html', dict(form=form))
