from dataclasses import dataclass
from typing import TypeAlias, Optional, Any, Callable

from act import will, returnly, temp, obj, via_indexer, reformer_of, I
from django.http import HttpRequest, HttpResponse

from access.confirmation import adapters
from access.confirmation import core
from shared.tools import name_enum_of
from shared.types import URL, Token, Password, Annotaton
from shared.transactions import Transaction, rollbackable


Subject: TypeAlias = adapters.Subject
Method: TypeAlias = adapters.Method
PortToken: TypeAlias = Token


@via_indexer
def SendingOf(id_annotation: Annotaton) -> temp:
    return temp(
        method=Method,
        by=Callable[adapters.EndpointOf[id_annotation], Callable[URL, Any]],
    )


@dataclass(frozen=True)
class Activation:
    subject: Subject
    method: Method
    token: PortToken
    password: Password


def activate_by(
    activation: Activation,
    request: HttpRequest,
) -> Optional[HttpResponse]:
    endpoint_of = rollbackable.optionally(adapters.endpoint_repository.get_of)

    with Transaction() as get_ok:
        result = core.activate_by(
            _from_activation_to_access(activation),
            endpoint_of=endpoint_of,
            handling_of=adapters.view_handler_payload_of(request),
            close=adapters.endpoint_repository.close,
        )

    return result if get_ok() else None


def registrate_for(subject: Subject, method: Method) -> reformer_of[
    adapters.ViewHandlerOf[I]
]:
    port = core.Port(subject, method)
    registrate = will(adapters.endpoint_handler_repository.registrate_for)(port)

    return returnly(registrate)


def open_port_of(
    subject: Subject,
    sending: SendingOf[I],
    *,
    for_: I,
) -> Optional[URL]:
    endpoint = core.Endpoint(
        adapters.generate_port_access_token(),
        core.Port(subject, sending.method),
        for_,
        adapters.generate_password(),
    )

    with Transaction() as get_ok:
        confirmation_page_url = core.open(
            endpoint,
            access_to=adapters.confirmation_page_url_of,
            sending_by=sending.by,
            save=adapters.endpoint_repository.save,
        )

    return confirmation_page_url if get_ok() else None


@name_enum_of
class subjects:
    authorization: Subject
    registration: Subject

    @name_enum_of
    class access_recovery:
        via_email: Subject
        via_name: Subject


@name_enum_of
class methods:
    email: Method


@obj.of
class via:
    email = obj(
        method=methods.email,
        by=rollbackable.binary(adapters.send_confirmation_mail_to),
    )


def _from_activation_to_access(
    activation: Activation,
) -> adapters.AccessToEndpoint:
    port = core.Port(activation.subject, activation.method)

    return core.AccessToEndpoint(activation.token, port, activation.password)
