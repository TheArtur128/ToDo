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

import confirmation
from access import payload
from access import services
from access.forms import (
    UserLoginForm, UserRegistrationForm, RestoringAccessByNameForm,
    RestoringAccessByEmailForm, ConfirmationForm
)
from access.utils import for_anonymous
from shared.models import User
from shared.tools import bad_or
from shared.types_ import Email, URL, ErrorMessage


@confirmation.payload.register_for(
    confirmation.payload.subjects.authorization,
    confirmation.payload.methods.email,
)
def authorization_confirmation(
    request: HttpRequest,
    email: Email,
) -> Optional[HttpResponse]:
    user = services.authorize_user_by(email, request=request)

    return None if user is None else redirect(reverse("tasks:index"))


@confirmation.payload.register_for(
    confirmation.payload.subjects.registration,
    confirmation.payload.methods.email,
)
def registration_confirmation(
    request: HttpRequest,
    email: Email,
) -> Optional[HttpResponse]:
    user = services.register_user_by(email, request=request)

    return None if user is None else redirect(reverse("tasks:index"))


@login_required
@require_GET
def logout(request: HttpRequest) -> HttpResponse:
    auth.logout(request)

    return redirect(reverse("tasks:index"))


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

        confirmation_page_url = confirmation.payload.open_port_of(
            confirmation.payload.subjects.authorization,
            confirmation.payload.via.email,
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

        confirmation_page_url = confirmation.payload.open_port_of(
            confirmation.payload.subjects.access_recovery.via_name,
            confirmation.payload.via.email,
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
