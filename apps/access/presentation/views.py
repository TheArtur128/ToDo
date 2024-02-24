from typing import Iterable

from act import bad, rwill, by
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.http import require_GET

from apps.access.adapters import controllers
from apps.access.core.types_ import Email, URL
from apps.access.presentation import ui, forms
from apps.access.lib import confirmation, for_anonymous, renders, messages_of


type _ErrorMesages = bad[Iterable[str]]


@confirmation.register_for(
    confirmation.subjects.authorization,
    confirmation.via.email,
)
def authorization_confirmation(
    request: HttpRequest,
    email: Email,
) -> HttpResponse | _ErrorMesages:
    try:
        controllers.authorization.complete_by(email, request)
    except ExceptionGroup as group:
        message_of = ui.authorization.completion.messages_of
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
        controllers.registration.complete_by(email, request)
    except ExceptionGroup as group:
        message_of = (
            ui.registration.completion.messages_of
            |by| reverse("access:sign-in")
        )
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
        controllers.access_recovery.complete_by(email, request)
    except ExceptionGroup as group:
        message_of = ui.access_recovery.completion.messages_of
        return bad(messages_of(group, message_of))

    return redirect(reverse("tasks:index"))


@login_required
@require_GET
def logout(request: HttpRequest) -> HttpResponse:
    auth.logout(request)

    return redirect(reverse("tasks:index"))


class _LoginView(confirmation.OpeningView):
    _form_type = forms.UserLoginForm
    _template_name = "access/login.html"

    @staticmethod
    def _open_port(request: HttpRequest) -> URL | bad[list[str]]:
        try:
            return controllers.authorization.open_using(
                name=request.POST["name"],
                password=request.POST["password"],
            )
        except ExceptionGroup as group:
            message_of = ui.authorization.opening.messages_of
            return bad(messages_of(group, message_of))


class _RegistrationView(confirmation.OpeningView):
    _form_type = forms.UserRegistrationForm
    _template_name = "access/registration.html"

    @staticmethod
    def _open_port(request: HttpRequest) -> URL | _ErrorMesages:
        try:
            return controllers.registration.open_using(
                request.POST["name"],
                request.POST["email"],
                request.POST["new_password"],
                request.POST["password_to_repeat"],
            )
        except ExceptionGroup as group:
            message_of = ui.registration.opening.messages_of
            message_of = rwill(message_of)(
                request.POST["name"],
                request.POST["email"],
            )
            return bad(messages_of(group, message_of))


class _AccessRecoveryView(confirmation.OpeningView):
    def _access_recovery(request: HttpRequest) -> URL:
        raise NotImplementedError

    def _open_port(self, request: HttpRequest) -> URL | _ErrorMesages:
        try:
            return self._access_recovery(request)
        except ExceptionGroup as group:
            message_of = ui.access_recovery.opening.messages_of
            return bad(messages_of(group, message_of))


class _AccessRecoveryByNameView(_AccessRecoveryView):
    _form_type = forms.RestoringAccessByNameForm
    _template_name = "access/recovery-by-name.html"

    @staticmethod
    def _access_recovery(request: HttpRequest) -> URL:
        return controllers.access_recovery.open_using_name(
            request.POST["name"],
            request.POST["new_password"],
        )


class _AccessRecoveryByEmailView(_AccessRecoveryView):
    _form_type = forms.RestoringAccessByEmailForm
    _template_name = "access/recovery-by-email.html"

    @staticmethod
    def _access_recovery(request: HttpRequest) -> URL:
        return controllers.access_recovery.open_using_email(
            request.POST["email"],
            request.POST["new_password"],
        )


@login_required
@require_GET
def profile(request: HttpRequest) -> HttpResponse:
    return renders.rendered(ui.profile.page_of(request.user), request)


registrate = for_anonymous(_RegistrationView.as_view())

login = for_anonymous(_LoginView.as_view())

restore_access_by_name = for_anonymous(_AccessRecoveryByNameView.as_view())

restore_access_by_email = for_anonymous(_AccessRecoveryByEmailView.as_view())
