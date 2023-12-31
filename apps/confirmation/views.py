from typing import Optional, Callable, Mapping

from act import bad
from django.forms import Form
from django.http import HttpRequest, HttpResponse, Http404
from django.shortcuts import redirect

from apps.confirmation import forms, services, types_, ui, lib


def confirm(
    request: HttpRequest,
    subject: services.Subject,
    method: services.Method,
    session_token: services.SessionToken,
) -> HttpResponse:
    if not ui.activation.is_valid_for(subject, method):
        raise Http404("incorrect subject or method")

    is_activation_failed = False

    if request.method == 'GET':
        form = forms.ConfirmationForm()
    else:
        form = forms.ConfirmationForm(data=request.POST)

    if request.method == "POST" and form.is_valid():
        response = services.endpoint.activate_by(
            subject=subject,
            method=method,
            session_token=session_token,
            activation_token=request.POST["token"],
            request=request,
        )

        if response is not None:
            return response

        is_activation_failed = True

    page = ui.activation.page_of(
        form,
        subject,
        method,
        session_token,
        is_activation_failed=is_activation_failed,
    )

    return lib.renders.rendered(page, request)


class OpeningView(lib.ViewWithForm):
    def _open_port(self, request: HttpRequest) -> Optional[types_.URL]:
        raise NotImplementedError

    def _service(
        self,
        *,
        request: HttpRequest,
        form: Form,
        render_with: Callable[Mapping, HttpResponse],
    ) -> HttpResponse | bad[list[types_.ErrorMessage]]:
        result = self._open_port(request)

        if result is None:
            return bad([ui.opening.failure_message])

        return redirect(result)
