from typing import Callable

from act import partially, Pm, Cn
from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect

from apps.access import input


confirmation = input.confirmation
renders = input.renders
ui = input.ui

User = input.User

hashed = input.hashed
unhashed = input.unhashed

half_hidden = input.half_hidden


@partially
def for_anonymous(
    view_action: Callable[Cn[HttpRequest, Pm], HttpResponse],
    *,
    redirect_to: str = settings.URL_TO_REDIRECT_NON_ANONYMOUS,
) -> Callable[Cn[HttpRequest, Pm], HttpResponse]:
    def wrapper(
        request: HttpRequest, *args: Pm.args, **kwargs: Pm.kwargs
    ) -> HttpResponse:
        return (
            redirect(redirect_to)
            if request.user.is_authenticated
            else view_action(request, *args, **kwargs)
        )

    return wrapper
