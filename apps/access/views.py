from typing import Optional

from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.http import require_GET

from apps.access import services
from apps.access.forms import (
    UserLoginForm, UserRegistrationForm, RestoringAccessByNameForm,
    RestoringAccessByEmailForm
)
from apps.access.input import confirmation
from apps.access.utils import for_anonymous
from apps.shared.types_ import Email, URL


@confirmation.register_for(
    confirmation.subjects.authorization,
    confirmation.via.email,
)
def authorization_confirmation(
    request: HttpRequest,
    email: Email,
) -> Optional[HttpResponse]:
    ok = services.authorization.complete_by(email, request=request)

    if not ok:
        return None

    return redirect(reverse("tasks:index"))


@confirmation.register_for(
    confirmation.subjects.registration,
    confirmation.via.email,
)
def registration_confirmation(
    request: HttpRequest,
    email: Email,
) -> Optional[HttpResponse]:
    ok = services.registration.complete_by(email, request=request)

    if not ok:
        return None

    return redirect(reverse("tasks:index"))


@login_required
@require_GET
def logout(request: HttpRequest) -> HttpResponse:
    auth.logout(request)

    return redirect(reverse("tasks:index"))


class LoginView(confirmation.OpeningView):
    _form_type = UserLoginForm
    _template_name = "pages/login.html"

    @staticmethod
    def _open_port(request: HttpRequest) -> Optional[URL]:
        confirmation_page_url = services.authorization.open_using(request)

        return confirmation_page_url


class _RegistrationView(confirmation.OpeningView):
    _form_type = UserRegistrationForm
    _template_name = "pages/registration.html"

    @staticmethod
    def _open_port(request: HttpRequest) -> Optional[URL]:
        confirmation_page_url = services.registration.open_using(request)

        return confirmation_page_url


class _AccessRecoveryByNameView(confirmation.OpeningView):
    _form_type = RestoringAccessByNameForm
    _template_name = "pages/access-recovery-by-name.html"

    @staticmethod
    def _open_port(request: HttpRequest) -> Optional[URL]:
        confirmation_page_url = services.access_recovery.open_via_name_using(
            request.POST["name"],
        )

        return confirmation_page_url


class _AccessRecoveryByEmailView(confirmation.OpeningView):
    _form_type = RestoringAccessByEmailForm
    _template_name = "pages/access-recovery-by-email.html"

    @staticmethod
    def _open_port(request: HttpRequest) -> Optional[URL]:
        confirmation_page_url = services.access_recovery.open_via_email_using(
            request.POST["email"],
        )

        return confirmation_page_url


registrate = for_anonymous(_RegistrationView.as_view())

login = for_anonymous(LoginView.as_view())

access_recovery_by_name = for_anonymous(_AccessRecoveryByNameView.as_view())

access_recovery_by_email = for_anonymous(_AccessRecoveryByEmailView.as_view())
