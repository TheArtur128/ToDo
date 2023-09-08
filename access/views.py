from typing import Type, TypeVar, Tuple, Optional, Callable, Mapping, Iterable

from act import of, bad, ok, v, _
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.forms import Form
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.views.decorators.http import require_GET

from core.models import User
from core.types import Email, URL
from access import confirmation
from access import services
from access.forms import (
    UserLoginForm, UserRegistrationForm, RestoringAccessByNameForm,
    RestoringAccessByEmailForm, ConfirmForm
)
from access.utils import for_anonymous


__all__ = (
    "login", "registrate", "logout", "access_recovery_by_name",
    "access_recovery_by_email"
)


def confirm(request: HttpRequest, subject: str, token: str) -> HttpResponse:
    errors = tuple()

    if request.method == 'GET':
        form = ConfirmForm()
    else:
        form = ConfirmForm(data=form.POST)
        id_group = request.POST.get("notified-via", None)

        if id_group is not None and form.is_valid():
            response = confirmation.activate(
                subject,
                token=token,
                id_group=id_group,
                password=form.POST["password"],
                request=request,
            )

            if response is not None:
                return response

            errors = ("Make sure you enter the correct password", )

    context = dict(
        subject=subject, form=form, errors=(*form.errors.values(), *errors)
    )

    return render(request, "pages/confirmation.html", context)


@confirmation.handle(confirmation.subjects.authorization, using=confirmation.id_groups.email)
def authorization_port(request: HttpRequest, email: Email) -> HttpResponse:
    user = User.objects.get(email=email)
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
        return render(
            request, self._template_name, dict(form=self._form_type())
        )

    def post(self, request: HttpRequest) -> HttpResponse:
        form = self._form_type(data=request.POST)
        render_with = (
            _.render(request, self._template_name, dict(form=form) | v)
        )

        if not form.is_valid():
            return render_with(dict(error_messages=tuple(form.errors.values())))

        result = self._service(
            request=request, form=form, render_with=render_with
        )

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


class _StaticPortOpeningView(ViewWithForm):
    _default_port_open_failure_message: str = (
        "Make sure you entered your account information correctly"
    )

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

    @staticmethod
    def _redirect_to(url: URL) -> HttpResponse | bad[None]:
        return bad(None) if url is None else redirect(url)

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


class LoginView(_StaticPortOpeningView):
    _form_type = UserLoginForm
    _template_name = "pages/login.html"

    def _open_port(self, request: HttpRequest) -> HttpResponse | bad[None]:
        user = auth.authenticate(
            request,
            username=request.POST["name"],
            password=request.POST["password"],
        )

        if user is None:
            return bad(None)

        confirmation_page_url = confirmation.open_email_port_of(
            confirmation.subjects.authorization, for_=request.POST["email"],
        )

        return self._redirect_to(confirmation_page_url)


class _RegistrationView(_StaticPortOpeningView):
    _form_type: Type[_FormT] = UserRegistrationForm
    _template_name: str = "pages/registration.html"

    def _open_port(self, request: HttpRequest) -> HttpResponse | bad[None]:
        confirmation_page_url = services.open_registration_port(
            name=request.POST["name"],
            email=request.POST["email"],
            password=request.POST["password1"],
        )

        return self._redirect_to(confirmation_page_url)


class _AccessRecoveryView(_StaticPortOpeningView):
    _default_port_open_success_message = (
        "Follow the link in the email you just received to recover access"
    )


class _AccessRecoveryByNameView(_AccessRecoveryView):
    _form_type = RestoringAccessByNameForm
    _template_name = "pages/access-recovery-by-name.html"

    def _open_port(self, request: HttpRequest) -> HttpResponse | bad[None]:
        user = User.objects.filter(name=request.POST["name"]).first()

        if user is None:
            return bad(None)

        confirmation_page_url = confirmation.open_email_port_of(
            confirmation.subjects.access_recovery.via_name, for_=user.email
        )

        return self._redirect_to(confirmation_page_url)


class _AccessRecoveryByEmailView(_AccessRecoveryView):
    _form_type = RestoringAccessByEmailForm
    _template_name = "pages/access-recovery-by-email.html"

    def _open_port(
        self,
        request: HttpRequest,
    ) -> ok[Optional[str]] | bad[Optional[str]]:
        confirmation_page_url = confirmation.open_email_port_of(
            confirmation.subjects.access_recovery.via_email,
            for_=request.POST["email"],
        )

        return self._redirect_to(confirmation_page_url)


registrate = for_anonymous(_RegistrationView.as_view())

login = for_anonymous(LoginView.as_view())

access_recovery_by_name = for_anonymous(_AccessRecoveryByNameView.as_view())

access_recovery_by_email = for_anonymous(_AccessRecoveryByEmailView.as_view())
