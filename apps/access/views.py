from typing import Optional

from act import bad
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.http import require_GET

from apps.access import errors, services, ui
from apps.access.forms import (
    UserLoginForm, UserRegistrationForm, RestoringAccessByNameForm,
    RestoringAccessByEmailForm
)
from apps.access.lib import confirmation, for_anonymous, renders, same_else
from apps.access.types_ import Email, URL


@confirmation.register_for(
    confirmation.subjects.authorization,
    confirmation.via.email,
)
def authorization_confirmation(
    request: HttpRequest,
    email: Email,
) -> Optional[HttpResponse]:
    ok = services.authorization.complete_by(email, request)

    return redirect(reverse("tasks:index")) if ok else None


@confirmation.register_for(
    confirmation.subjects.registration,
    confirmation.via.email,
)
def registration_confirmation(
    request: HttpRequest,
    email: Email,
) -> HttpResponse | bad[list[str]]:
    try:
        services.registration.complete_by(email, request)
    except errors.Access as error:
        message = ui.registration.completion.error_message_of(error)
        return bad([same_else(error, message)])

    return redirect(reverse("tasks:index"))


@confirmation.register_for(
    confirmation.subjects.access_recovery,
    confirmation.via.email,
)
def access_recovery_confirmation(
    request: HttpRequest,
    email: Email,
) -> Optional[HttpResponse]:
    ok = services.access_recovery.complete_by(email, request)

    return redirect(reverse("tasks:index")) if ok else None


@login_required
@require_GET
def logout(request: HttpRequest) -> HttpResponse:
    auth.logout(request)

    return redirect(reverse("tasks:index"))


class LoginView(confirmation.OpeningView):
    _form_type = UserLoginForm
    _template_name = "access/login.html"

    @staticmethod
    def _open_port(request: HttpRequest) -> Optional[URL]:
        confirmation_page_url = services.authorization.open_using(
            request.POST["username"],
            request.POST["password"],
            request,
        )

        return confirmation_page_url


class _RegistrationView(confirmation.OpeningView):
    _form_type = UserRegistrationForm
    _template_name = "access/registration.html"

    @staticmethod
    def _open_port(request: HttpRequest) -> URL | bad[list[str]]:
        try:
            confirmation_page_url = services.registration.open_using(
                name=request.POST["name"],
                email=request.POST["email"],
                password=request.POST["password1"],
            )
        except errors.Access as error:
            message = ui.registration.opening.error_message_of(
                error,
                request.POST["name"],
            )
            return bad([same_else(error, message)])

        return confirmation_page_url


class _AccessRecoveryByNameView(confirmation.OpeningView):
    _form_type = RestoringAccessByNameForm
    _template_name = "access/recovery-by-name.html"

    @staticmethod
    def _open_port(request: HttpRequest) -> Optional[URL]:
        confirmation_page_url = services.access_recovery.open_via_name_using(
            request.POST["name"],
            request.POST["password1"],
        )

        return confirmation_page_url


class _AccessRecoveryByEmailView(confirmation.OpeningView):
    _form_type = RestoringAccessByEmailForm
    _template_name = "access/recovery-by-email.html"

    @staticmethod
    def _open_port(request: HttpRequest) -> Optional[URL]:
        confirmation_page_url = services.access_recovery.open_via_email_using(
            request.POST["email"],
            request.POST["password1"],
        )

        return confirmation_page_url


@login_required
@require_GET
def profile(request: HttpRequest) -> HttpResponse:
    return renders.rendered(services.profile.of(request.user), request)


registrate = for_anonymous(_RegistrationView.as_view())

login = for_anonymous(LoginView.as_view())

restore_access_by_name = for_anonymous(_AccessRecoveryByNameView.as_view())

restore_access_by_email = for_anonymous(_AccessRecoveryByEmailView.as_view())
