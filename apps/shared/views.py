from typing import Callable, Mapping, Type, Iterable

from act import bad, of, fun
from act.cursors.static import v, _
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.generic import View

from apps.shared.types_ import ErrorMessage, FormT


class ViewWithForm(View):
    form_type = property(fun(v._form_type))
    template_name = property(v._template_name)

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(
            request, self._template_name, dict(form=self._form_type())
        )

    def post(self, request: HttpRequest) -> HttpResponse:
        form = self._form_type(data=request.POST)
        render_with = fun(
            _.render(request, self._template_name, dict(form=form) | v)
        )

        if not form.is_valid():
            return render_with(dict(errors=tuple(form.errors.values())))

        result = self._service(
            request=request, form=form, render_with=render_with
        )

        if of(bad, result):
            return render_with(dict(errors=tuple(result.value)))

        return result

    _form_type: Type[FormT]
    _template_name: str

    def _service(
        self,
        *,
        request: HttpRequest,
        form: FormT,
        render_with: Callable[Mapping, HttpResponse]
    ) -> HttpResponse | bad[Iterable[ErrorMessage]]:
        raise NotImplementedError
