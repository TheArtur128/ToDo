from typing import Optional, Callable, Mapping

from act import bad
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect

from confirmation import services, forms
from shared import views, types_


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


class OpeningView(views.ViewWithForm):
    _failure_message: types_.ErrorMessage = (
        "Make sure you have entered your information correctly"
    )

    def _open_port(self, request: HttpRequest) -> Optional[types_.URL]:
        raise NotImplementedError

    def _service(
        self,
        *,
        request: HttpRequest,
        render_with: Callable[Mapping, HttpResponse],
    ) -> HttpResponse | list[bad[types_.ErrorMessage]]:
        result = self._open_port(request)

        if result is None:
            return [bad(self._failure_message)]

        return redirect(result)
