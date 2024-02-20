from act import bad, by
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
from apps.access.lib import confirmation, for_anonymous, renders, messages_of
from apps.access.types_ import Email, URL


type _ErrorMesages = bad[tuple[str]]


@confirmation.register_for(
    confirmation.subjects.authorization,
    confirmation.via.email,
)
def authorization_confirmation(
    request: HttpRequest,
    email: Email,
) -> HttpResponse | _ErrorMesages:
    try:
        services.authorization.complete_by(email, request)
    except* errors.Access as group:
        message_of = ui.authorization.completion.error_message_of
        return bad(messages_of(group, message_of))

    return redirect(reverse("tasks:index"))


@confirmation.register_for(
    confirmation.subjects.registration,
    confirmation.via.email,
)
def registration_confirmation(
    request: HttpRequest,
    email: Email,
) -> HttpResponse | _ErrorMesages:
    try:
        services.registration.complete_by(email, request)
    except* errors.Access as group:
        message_of = ui.registration.completion.error_message_of
        return bad(messages_of(group, message_of))

    return redirect(reverse("tasks:index"))


@confirmation.register_for(
    confirmation.subjects.access_recovery,
    confirmation.via.email,
)
def access_recovery_confirmation(
    request: HttpRequest,
    email: Email,
) -> HttpResponse | _ErrorMesages:
    try:
        services.access_recovery.complete_by(email, request)
    except* errors.Access as group:
        message_of = ui.access_recovery.completion.error_message_of
        return bad(messages_of(group, message_of))

    return redirect(reverse("tasks:index"))


@login_required
@require_GET
def logout(request: HttpRequest) -> HttpResponse:
    auth.logout(request)

    return redirect(reverse("tasks:index"))


class LoginView(confirmation.OpeningView):
    _form_type = UserLoginForm
    _template_name = "access/login.html"

    @staticmethod
    def _open_port(request: HttpRequest) -> URL | bad[list[str]]:
        try:
            return services.authorization.open_using(
                request.POST["username"],
                request.POST["password"],
                request,
            )
        except* errors.Access as group:
            message_of = ui.authorization.opening.error_message_of
            return bad(messages_of(group, message_of))


class _RegistrationView(confirmation.OpeningView):
    _form_type = UserRegistrationForm
    _template_name = "access/registration.html"

    @staticmethod
    def _open_port(request: HttpRequest) -> URL | _ErrorMesages:
        try:
            return services.registration.open_using(
                name=request.POST["name"],
                email=request.POST["email"],
                password=request.POST["password1"],
            )
        except* errors.Access as group:
            message_of = ui.registration.opening.error_message_of
            return bad(messages_of(group, message_of |by| request.POST["name"]))


class _AccessRecoveryView(confirmation.OpeningView):
    def _access_recovery(request: HttpRequest) -> URL:
        raise NotImplementedError

    def _open_port(self, request: HttpRequest) -> URL | _ErrorMesages:
        try:
            return self._access_recovery(request)
        except* errors.Access as group:
            message_of = ui.access_recovery.opening.error_message_of
            return bad(messages_of(group, message_of))


class _AccessRecoveryByNameView(_AccessRecoveryView):
    _form_type = RestoringAccessByNameForm
    _template_name = "access/recovery-by-name.html"

    @staticmethod
    def _access_recovery(request: HttpRequest) -> URL:
        return services.access_recovery.open_via_name_using(
            request.POST["name"],
            request.POST["password1"],
        )


class _AccessRecoveryByEmailView(_AccessRecoveryView):
    _form_type = RestoringAccessByEmailForm
    _template_name = "access/recovery-by-email.html"

    @staticmethod
    def _access_recovery(request: HttpRequest) -> URL:
        return services.access_recovery.open_via_email_using(
            request.POST["email"],
            request.POST["password1"],
        )


@login_required
@require_GET
def profile(request: HttpRequest) -> HttpResponse:
    return renders.rendered(ui.profile.page_of(request.user), request)


registrate = for_anonymous(_RegistrationView.as_view())

login = for_anonymous(LoginView.as_view())

restore_access_by_name = for_anonymous(_AccessRecoveryByNameView.as_view())

restore_access_by_email = for_anonymous(_AccessRecoveryByEmailView.as_view())
