from django.shortcuts import render, HttpResponseRedirect
from django.contrib import auth

from accounts.forms import UserLoginForm

    if request.method == 'GET':
        form = UserLoginForm()

def login(request):
    elif request.method == 'POST':
        form = UserLoginForm(data=request.POST)

        if form.is_valid():
            user = auth.authenticate(
                request,
                username=request.POST['username'],
                password=request.POST['password'],
            )

            if user:
                auth.login(request, user)

                return redirect(reverse('tasks:index'))

    return render(request, 'login.html', dict(form=form))
