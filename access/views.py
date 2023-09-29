from typing import Optional

from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.http import require_GET

from access import services
from access.forms import (
    UserLoginForm, UserRegistrationForm, RestoringAccessByNameForm,
    RestoringAccessByEmailForm
)
from access.input import confirmation
from access.utils import for_anonymous
from shared.models import User
from shared.transactions import do, rollbackable, Do
from shared.types_ import Email, URL


@confirmation.register_for(
    confirmation.subjects.authorization,
    confirmation.methods.email,
)
def authorization_confirmation(
    request: HttpRequest,
    email: Email,
) -> Optional[HttpResponse]:
    user = services.authorize_by(email, request=request)

    if user is None:
        return None

    return redirect(reverse("tasks:index"))


@confirmation.register_for(
    confirmation.subjects.registration,
    confirmation.methods.email,
)
def registration_confirmation(
    request: HttpRequest,
    email: Email,
) -> Optional[HttpResponse]:
    user = services.register_by(email, request=request)

    if user is None:
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
        confirmation_page_url = services.authorization_by(request)

        return confirmation_page_url


class _RegistrationView(confirmation.OpeningView):
    _form_type = UserRegistrationForm
    _template_name = "pages/registration.html"

    @staticmethod
    @do(rollbackable.optionally)
    def _open_port(do: Do, request: HttpRequest) -> URL:
        user = User(
            name=request.POST["name"],
            email=request.POST["email"],
            password=request.POST["password1"],
        )

        confirmation_page_url = do(services.open_registration_port_for(user))

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
