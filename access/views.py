from typing import Type, TypeVar, Tuple, Optional

from act import of, bad, ok, v, _
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
from access.services import open_authorization_port_for
from access.tools import status_of
from access.utils import for_anonymous
from tasks.models import User


__all__ = (
    "login", "registrate", "authorize", "logout", "access_recovery_by_name",
    "access_recovery_by_email"
)


def confirm(request: HttpRequest, subject: str) -> HttpResponse:
    errors = tuple()

    if request.method == 'GET':
        form = ConfirmForm()
    else:
        form = ConfirmForm(data=form.POST)

        if form.is_valid():
            is_port_open = open_port_of(subject, for_=form.POST["email"])

            if is_port_open:
                return redirect(confirmation_page_url_of(subject))

            errors = ("", )

    context = dict(
        subject=subject, form=form, errors=(*form.errors.values(), *errors)
    )

    return render(request, "pages/confirmation.html", context)


@for_anonymous
@require_GET
def authorize(request: HttpRequest, token: str) -> HttpResponse:
    email = port_email_of("authorization").get_of(token)

    if email is not None:
        user = User.objects.get(email=email)

        if not user.is_active:
            user.is_active = True

            user.save()

        delete_of(token, "authorization")

        auth.login(request, user)

    return redirect(reverse("tasks:index"))


@login_required
@require_GET
def logout(request: HttpRequest) -> HttpResponse:
    auth.logout(request)

    return redirect(reverse("tasks:index"))


_FormT = TypeVar("_FormT", bound=Form)


class ViewWithForm(View):
    form_type = property(v._form_type)
    template_name = property(v._template_name)

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, self._template_name, dict(form=self._form_type()))

    def post(self, request: HttpRequest) -> HttpResponse:
        form = self._form_type(data=request.POST)
        render_with = (
            _.render(request, self._template_name, dict(form=form) | v)
        )

        if not form.is_valid():
            return render_with(dict(error_messages=tuple(form.errors.values())))

        result = self._service(request=request, form=form, render_with=render_with)

        if of(bad, result):
            return render_with(dict(error_messages=tuple(result.value)))

        return result

    _form_type: Type[_FormT]
    _template_name: str

    def _service(
        self,
        *,
        request: HttpRequest,
        form: _FormT,
        render_with: Callable[Mapping, HttpResponse]
    ) -> HttpResponse | bad[Iterable[str]]:
        raise NotImplementedError


class LoginView(ViewWithForm):
    _form_type = UserLoginForm
    _template_name = "pages/login.html"

    def _service(
        self,
        *,
        request: HttpRequest,
        form: UserLoginForm,
        render_with: Callable[Mapping, HttpResponse]
    ) -> HttpResponse | bad[Iterable[str]]:
        is_port_open = open_port_of(subject, for_=form.POST["email"])

        if is_port_open:
            return redirect(confirmation_page_url_of(subject))

        user = auth.authenticate(
            request,
            username=request.POST["name"],
            password=request.POST["password"],
        )

        if user:
            auth.login(request, user)

            return redirect(reverse("tasks:index"))


class _RegistrationView(ViewWithForm):
    _form_type: Type[_FormT] = UserRegistrationForm
    _template_name: str = "pages/registration.html"

    def _service(
        self,
        *,
        request: HttpRequest,
        form: UserRegistrationForm,
        render_with: Callable[Mapping, HttpResponse],
    ) -> HttpResponse:
        user_data = obj(
            name=request.POST["name"],
            email=request.POST["email"],
            password=request.POST["password1"]
        )

        is_port_open = open_registration_port_for(
            user_data, request=request
        )

        if is_port_open:
            return redirect(reverse("access:registration_port"))
        else:
            return bad(
                ["Make sure the email is correct or try again after a while"]
            )


class _StaticPortOpeningView(ViewWithForm):
    def _service(
        self,
        *,
        request: HttpRequest,
        render_with: Callable[Mapping, HttpResponse]
    ) -> HttpResponse:
        return render_with(self.__context_about(self._open_port(request)))

    def _open_port(
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
            else "error_messages"
        )

        if of(ok, port_open_message):
            message_subject = "notification_messages"
            default_message = self._default_port_open_success_message
        else:
            message_subject = "error_messages"
            default_message = self._default_port_open_failure_message

        final_message = (
            default_message
            if port_open_message.value is None
            else port_open_message.value
        )

        return {message_subject: (final_message, )}


class _AccessRecoveryView(_StaticPortOpeningView):
    _default_port_open_success_message = (
        "Follow the link in the email you just received to recover access"
    )
    _default_port_open_failure_message: str = (
        "Make sure the email is correct or try again after a while"
    )


class _AccessRecoveryByNameView(_AccessRecoveryView):
    _form_type = RestoringAccessByNameForm
    _template_name = "pages/access-recovery-by-name.html"

    def _open_port(
        self,
        request: HttpRequest,
    ) -> ok[Optional[str]] | bad[Optional[str]]:
        user = User.objects.filter(name=request.POST["name"]).first()

        if user is None:
            return bad("There is no user with this name")

        return status_of(open_authorization_port_for(
            user.email,
            request=request)
        )


class _AccessRecoveryByEmailView(_AccessRecoveryView):
    _form_type = RestoringAccessByEmailForm
    _template_name = "pages/access-recovery-by-email.html"

    def _open_port(
        self,
        request: HttpRequest,
    ) -> ok[Optional[str]] | bad[Optional[str]]:
        return status_of(open_authorization_port_for(
            request.POST["email"],
            request=request,
        ))


registrate = for_anonymous(_RegistrationView.as_view())

login = for_anonymous(LoginView.as_view())

access_recovery_by_name = for_anonymous(_AccessRecoveryByNameView.as_view())

access_recovery_by_email = for_anonymous(_AccessRecoveryByEmailView.as_view())