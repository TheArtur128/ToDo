from typing import Optional, Callable, Mapping

from act import of, bad, ok, v, saving_context, on, _
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect

from confirmation import services, forms
from shared.types_ import URL, ErrorMessage


def confirm(
    request: HttpRequest,
    subject: services.Subject,
    method: services.Method,
    token: services.PortToken,
) -> HttpResponse:
    errors = tuple()

    if request.method == 'GET':
        form = forms.ConfirmationForm()
    else:
        form = forms.ConfirmationForm(data=form.POST)

        if form.is_valid():
            activation = services.Activation(
                subject, method, token, request.POST["password"]
            )
            response = services.activate_by(activation, request)

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


class ConfirmationOpeningView(shared.views.ViewWithForm):
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
