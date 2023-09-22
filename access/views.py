from typing import Type, TypeVar, Optional, Callable, Mapping, Iterable

from act import of, bad, ok, v, saving_context, on, _
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.forms import Form
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.views.decorators.http import require_GET

from access import confirmation
from access import services
from access.forms import (
    UserLoginForm, UserRegistrationForm, RestoringAccessByNameForm,
    RestoringAccessByEmailForm, ConfirmationForm
)
from access.utils import for_anonymous
from shared.models import User
from shared.tools import bad_or
from shared.types_ import Email, URL, ErrorMessage


__all__ = (
    "confirm", "login", "registrate", "logout", "access_recovery_by_name",
    "access_recovery_by_email"
)


def confirm(
    request: HttpRequest,
    subject: confirmation.facade.Subject,
    method: confirmation.facade.Method,
    token: confirmation.facade.PortToken,
) -> HttpResponse:
    errors = tuple()

    if request.method == 'GET':
        form = ConfirmationForm()
    else:
        form = ConfirmationForm(data=form.POST)

        if form.is_valid():
            activation = confirmation.facade.Activation(
                subject, method, token, request.POST["password"]
            )
            response = confirmation.facade.activate_by(activation, request)

            if response is not None:
                return response

            errors = [
                "You entered the wrong password"
                f" or the {subject} time has expired"
            ]

    context = dict(
        subject=subject, form=form, errors=(*form.errors.values(), *errors)
    )

    return render(request, "pages/confirmation.html", context)


@confirmation.facade.registrate_for(
    confirmation.facade.subjects.authorization,
    confirmation.facade.methods.email,
)
def authorization_confirmation(
    request: HttpRequest,
    email: Email,
) -> HttpResponse:
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
            return render_with(dict(errors=tuple(form.errors.values())))

        result = self._service(
            request=request, form=form, render_with=render_with
        )

        if of(bad, result):
            return render_with(dict(errors=tuple(result.value)))

        return result

    _form_type: Type[_FormT]
    _template_name: str

    def _service(
        self,
        *,
        request: HttpRequest,
        form: _FormT,
        render_with: Callable[Mapping, HttpResponse]
    ) -> HttpResponse | bad[Iterable[ErrorMessage]]:
        raise NotImplementedError


class _ConfirmationOpeningView(ViewWithForm):
    _default_confirmation_open_failure_message: ErrorMessage = (
        "Make sure you have entered your information correctly"
    )

    def _open_port(
        self,
        request: HttpRequest,
    ) -> ok[URL] | bad[Optional[ErrorMessage]]:
        raise NotImplementedError

    def _service(
        self,
        *,
        request: HttpRequest,
        render_with: Callable[Mapping, HttpResponse],
    ) -> HttpResponse:
        result = self._open_port(request)

        if of(ok, result):
            return redirect(result.value)

        default_message = self._default_confirmation_open_failure_message

        return saving_context(on(None, default_message))(result)


class LoginView(_ConfirmationOpeningView):
    _form_type = UserLoginForm
    _template_name = "pages/login.html"

    @staticmethod
    def _open_port(request: HttpRequest) -> URL | bad[Optional[ErrorMessage]]:
        user = auth.authenticate(
            request,
            username=request.POST["name"],
            password=request.POST["password"],
        )

        if user is None:
            return bad(None)

        confirmation_page_url = confirmation.facade.open_port_of(
            confirmation.facade.subjects.authorization,
            confirmation.facade.via.email,
            for_=request.POST["email"],
        )

        return bad_or(confirmation_page_url)


class _RegistrationView(_ConfirmationOpeningView):
    _form_type = UserRegistrationForm
    _template_name = "pages/registration.html"

    @staticmethod
    def _open_port(request: HttpRequest) -> URL | bad[Optional[ErrorMessage]]:
        # Not implemented
        confirmation_page_url = services.open_registration_port(
            name=request.POST["name"],
            email=request.POST["email"],
            password=request.POST["password1"],
        )

        return bad_or(confirmation_page_url)


class _EmailAccessRecoveryView(_ConfirmationOpeningView):
    _form_type = RestoringAccessByNameForm
    _template_name = "pages/access-recovery-by-name.html"

    def _user_of(self, request: HttpRequest) -> Optional[User]:
        raise NotImplementedError

    def _open_port(
        self,
        request: HttpRequest,
    ) -> URL | bad[Optional[ErrorMessage]]:
        user = self._user_of(request)

        if user is None:
            return bad(None)

        confirmation_page_url = confirmation.facade.open_port_of(
            confirmation.facade.subjects.access_recovery.via_name,
            confirmation.facade.via.email,
            for_=user.email,
        )

        return bad_or(confirmation_page_url)


class _AccessRecoveryByNameView(_ConfirmationOpeningView):
    _form_type = RestoringAccessByNameForm
    _template_name = "pages/access-recovery-by-name.html"

    @staticmethod
    def _user_of(request: HttpRequest) -> Optional[User]:
        return User.objects.filter(name=request.POST["name"]).first()


class _AccessRecoveryByEmailView(_ConfirmationOpeningView):
    _form_type = RestoringAccessByEmailForm
    _template_name = "pages/access-recovery-by-email.html"

    @staticmethod
    def _user_of(request: HttpRequest) -> Optional[User]:
        return User.objects.filter(email=request.POST["email"]).first()


registrate = for_anonymous(_RegistrationView.as_view())

login = for_anonymous(LoginView.as_view())

access_recovery_by_name = for_anonymous(_AccessRecoveryByNameView.as_view())

access_recovery_by_email = for_anonymous(_AccessRecoveryByEmailView.as_view())
