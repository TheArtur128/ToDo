from typing import Optional, Callable, Mapping

from act import bad
from django.forms import Form
from django.http import HttpRequest, HttpResponse, Http404
from django.shortcuts import render, redirect

from apps.confirmation import services, forms, ui
from apps.shared import views, types_


def confirm(
    request: HttpRequest,
    subject: services.Subject,
    method: services.Method,
    token: services.SessionToken,
) -> HttpResponse:
    if not ui.is_valid(subject, method):
        raise Http404("incorrect subject or method")

    errors = tuple()

    if request.method == 'GET':
        form = forms.ConfirmationForm()
    else:
        form = forms.ConfirmationForm(data=request.POST)

        if form.is_valid():
            response = services.endpoint.activate_by(
                subject=subject,
                method=method,
                session_token=token,
                password=request.POST["password"],
                request=request,
            )

            if response is not None:
                return response

            errors = [
                "You entered the wrong password"
                f" or the {subject} time has expired"
            ]

    context = dict(
        subject=subject,
        method=method,
        token=token,
        form=form,
        errors=(*form.errors.values(), *errors),
    )

    return render(request, "confirmation/pages/confirmation.html", context)


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
        form: Form,
        render_with: Callable[Mapping, HttpResponse],
    ) -> HttpResponse | bad[list[types_.ErrorMessage]]:
        result = self._open_port(request)

        if result is None:
            return bad([self._failure_message])

        return redirect(result)
