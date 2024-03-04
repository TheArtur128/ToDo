from typing import Callable

from act import val, partially, Pm, Cn
from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from event_bus import EventBus

from apps.confirmation import output as confirmation
from apps.shared import errors, mixins, types_, validation, event_bus


confirmation = confirmation


event_bus: EventBus = event_bus.event_bus


messages_of = errors.messages_of


mixins = val(Visualizable=mixins.Visualizable)


Sculpture = types_.Sculpture


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
