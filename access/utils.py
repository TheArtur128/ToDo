from typing import Callable, Concatenate

from act import partially, Pm
from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect


__all__ = ("for_anonymous", )


@partially
def for_anonymous(
    view_action: Callable[Concatenate[HttpRequest, Pm], HttpResponse],
    *,
    redirect_to: str = settings.URL_TO_REDIRECT_NON_ANONYMOUS,
) -> Callable[Concatenate[HttpRequest, Pm], HttpResponse]:
    def wrapper(request: HttpRequest, *args: Pm.args, **kwargs: Pm.kwargs) -> HttpResponse:
        return (
            redirect(redirect_to)
            if request.user.is_authenticated
            else view_action(request, *args, **kwargs)
        )

    return wrapper
