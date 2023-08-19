from typing import Type, TypeVar, Tuple

from act import of, bad, ok
from django.core.cache import caches
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.forms import Form
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.views.decorators.http import require_GET

from access.forms import (
    UserLoginForm, UserRegistrationForm, RestoringAccessByNameForm,
    RestoringAccessByEmailForm
)
from access.services import (
    account_activation_by, recover_access_by_name, recover_access_by_email
)
from tasks.models import User


def login(request: HttpRequest) -> HttpResponse:
    if request.method == 'GET':
        form = UserLoginForm()

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


def registrate(request: HttpRequest) -> HttpResponse:
    was_registered = False
    errors = tuple()

    if request.method == 'GET':
        form = UserRegistrationForm()

    elif request.method == 'POST':
        form = UserRegistrationForm(data=request.POST)

        if form.is_valid():
            result = account_activation_by(
                request.POST['email'],
                request=request,
            )

            if not of(bad, result):
                was_registered = True

                user = form.save()
                auth.login(request, user)
            else:
                errors = (result.value, )

    context = dict(
        form=form,
        errors=errors if errors else tuple(form.errors.values()),
        was_registered=was_registered,
    )

    return render(request, 'registration.html', context)


@require_GET
def authorize(request: HttpRequest, token: str) -> HttpResponse:
    email = caches['emails-to-confirm'].get(token)

    if email is not None:
        user = User.objects.get(email=email)

        if not user.is_active:
            user.is_active = True

            user.save()

        caches['emails-to-confirm'].delete(token)

        auth.login(request, user)

    return redirect(reverse('tasks:index'))


@login_required
@require_GET
def logout(request: HttpRequest) -> HttpResponse:
    auth.logout(request)

    return redirect(reverse('tasks:index'))


_FormT = TypeVar("_FormT", bound=Form)


class AccessRecoveryView(View):
    form_type: Type[_FormT]
    template_name: str

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, self.template_name, dict(form=self.form_type()))

    def post(self, request: HttpRequest) -> HttpResponse:
        form = self.form_type(data=request.POST)

        return (
            render(
                request,
                self.template_name,
                dict(form=form) | self._messages_of(self.service(request)),
            )
            if form.is_valid()
            else render(
                request,
                self.template_name,
                dict(form=form, error_messages=tuple(form.errors.values())),
            )
        )

    def service(self, request) -> ok[str] | bad[str]:
        raise NotImplementedError

    @staticmethod
    def _messages_of(value: ok[str] | bad[str]) -> dict[str,  Tuple[str]]:
        key = 'notification_messages' if of(ok, value) else 'error_messages'

        return {key: (value.value, )}


class AccessRecoveryByNameView(AccessRecoveryView):
    form_type = RestoringAccessByNameForm
    template_name = 'access-recovery-by-name.html'

    def service(self, request: HttpRequest) -> ok[str] | bad[str]:
        return recover_access_by_name(request.POST['name'], request=request)


class AccessRecoveryByEmailView(AccessRecoveryView):
    form_type = RestoringAccessByEmailForm
    template_name = 'access-recovery-by-email.html'

    def service(self, request: HttpRequest) -> ok[str] | bad[str]:
        return recover_access_by_email(request.POST['email'], request=request)
