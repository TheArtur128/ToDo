from typing import Callable, Any

from act import will, via_indexer, temp, obj, reformer_of, I

from confirmation import adapters, cases, services, views
from shared.tools import name_enum_of, io
from shared.types_ import Annotaton, URL, Email
from shared.transactions import rollbackable, do, Do


@via_indexer
def _SendingOf(id_annotation: Annotaton) -> temp:
    return temp(
        method=services.Method,
        by=Callable[adapters.EndpointOf[id_annotation], Callable[URL, Any]],
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
        by=rollbackable.binary(adapters.send_confirmation_mail_to),
    )


def register_for(
    subject: services.Subject,
    method: services.Method,
) -> reformer_of[adapters.ViewHandlerOf[I]]:
    port = adapters.Port(subject, method)
    registrate = will(adapters.endpoint_handler_repository.register_for)(port)

    return io(registrate)


@do()
def open_port_of(
    do: Do,
    subject: services.Subject,
    sending: _SendingOf[I],
    *,
    for_: I,
) -> URL:
    endpoint = adapters.Endpoint(
        adapters.generate_port_access_token(),
        adapters.Port(subject, sending.method),
        for_,
        adapters.generate_password(),
    )

    opned_endpoint = cases.opened(
        endpoint,
        access_to=adapters.confirmation_page_url_of,
        sending_by=do(sending.by),
        saving_for=adapters.endpoint_repository.save,
    )

    return opned_endpoint.access_to


OpeningView = views.OpeningView