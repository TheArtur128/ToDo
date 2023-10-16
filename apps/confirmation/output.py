from typing import Callable, Any

from act import (
    to, via_indexer, temp, obj, name_enum_of, io, rollbackable, do, Do,
    reformer_of, I, Annotation
)

from apps.confirmation import adapters, cases, services, views
from apps.shared.types_ import URL, Email


@via_indexer
def _SendingOf(id_annotation: Annotation) -> temp:
    return temp(
        method=services.Method,
        by=Callable[adapters.Endpoint[id_annotation], Callable[URL, Any]],
    )


@name_enum_of
class subjects:
    authorization: services.Subject
    registration: services.Subject
    access_recovery: services.Subject


@name_enum_of
class _methods:
    email: services.Method


@obj.of
class via:
    email: _SendingOf[Email] = obj(
        method=_methods.email,
        by=rollbackable.binary(adapters.send_confirmation_mail_by),
    )


def register_for(
    subject: services.Subject,
    send: _SendingOf[I],
) -> reformer_of[adapters.HandlerOf[I]]:
    port = adapters.Port(subject, send.method)
    registrate = adapters.handler_repository.save_for |to| port

    return io(registrate)


@do(else_=None)
def open_port_of(
    do: Do,
    subject: services.Subject,
    send: _SendingOf[I],
    *,
    for_: I,
) -> URL:
    confirmation_page_url = cases.endpoint.open_for(
        adapters.Port(subject, send.method),
        for_,
        generate_activation_code=adapters.generate_activation_code,
        endpoint_for=adapters.Endpoint,
        send_access_of=do(send.by),
        save=adapters.endpoint_repository.save,
    )

    return confirmation_page_url.value


OpeningView = views.OpeningView
