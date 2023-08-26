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
    authorization_port_for, recover_access_by_name, recover_access_by_email
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
            is_port_open = open_authorization_port_for(
                request.POST["email"],
                request=request)

            if not is_port_open:
                errors = (result.value, )
            else:
                was_registered = True

                user = form.save()
                auth.login(request, user)

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

    __default_port_open_success_message: str = (
        "Follow the link in the email you just received to recover access")

    __default_port_open_failure_message: str = (
        "Make sure the email is correct or try again after a while")

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, self.template_name, dict(form=self.form_type()))

    def post(self, request: HttpRequest) -> HttpResponse:
        form = self.form_type(data=request.POST)
        render_with = partial(render, request, self.template_name)

        return (
            render_with(
                dict(form=form)
                | self.__context_about(self._open_recovery_port(request)))
            if form.is_valid()
            render_with(dict(
                form=form,
                error_messages=tuple(form.errors.values())))
        )

    def _open_recovery_port(
        self,
        request: HttpRequest,
    ) -> ok[Optional[str]] | bad[Optional[str]]:
        raise NotImplementedError

    def __context_about(
        self,
        port_open_message: ok[Optional[str]] | bad[Optional[str]]
    ) -> dict[str,  Tuple[str]]:
        message_subject = (
            "notification_messages"
            if of(ok, port_open_message)
            else "error_messages")

        if of(ok, port_open_message):
            message_subject = "notification_messages"
            default_message = self.__default_port_open_success_message
        else:
            message_subject = "error_messages"
            default_message = self.__default_port_open_failure_message

        final_message = (
            default_message
            if port_open_message.value is None
            else port_open_message.value)

        return {message_subject: (final_message, )}


class AccessRecoveryByNameView(AccessRecoveryView):
    form_type = RestoringAccessByNameForm
    template_name = "pages/access-recovery-by-name.html"

    def _open_recovery_port(
        self,
        request: HttpRequest,
    ) -> ok[Optional[str]] | bad[Optional[str]]:
        user = User.objects.filter(name=request.POST["name"]).first()

        if user is None:
            return bad("There is no user with this name")

        return status_of(open_authorization_port_for(
            user.email,
            request=request))


class AccessRecoveryByEmailView(AccessRecoveryView):
    form_type = RestoringAccessByEmailForm
    template_name = "pages/access-recovery-by-email.html"

    def _open_recovery_port(
        self,
        request: HttpRequest,
    ) -> ok[Optional[str]] | bad[Optional[str]]:
        return status_of(open_authorization_port_for(
            request.POST["email"],
            request=request))
