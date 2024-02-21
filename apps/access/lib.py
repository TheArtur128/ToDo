from typing import Callable

from act import partially, Pm, Cn
from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect

from apps.confirmation import output as confirmation
from apps.tasks import output as tasks
from apps.shared import errors, models, renders, lib, ui, types_, validation


Sculpture = types_.Sculpture
Application = errors.Application

confirmation = confirmation
renders = renders
ui = ui

User = models.User
created_user_of = tasks.created_user_of

half_hidden = lib.half_hidden

messages_of = errors.messages_of

to_raise_multiple_errors = validation.to_raise_multiple_errors
last = validation.last
latest = validation.latest

same = validation.same
exists = validation.exists

valid = validation.valid



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
