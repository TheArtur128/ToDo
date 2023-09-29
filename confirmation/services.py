from dataclasses import dataclass
from typing import TypeAlias, Optional

from django.http import HttpRequest, HttpResponse

from confirmation import adapters, cases
from shared.transactions import do, rollbackable, Do
from shared.types_ import Token, Password


Subject: TypeAlias = adapters.Subject
Method: TypeAlias = adapters.Method
PortToken: TypeAlias = Token


@dataclass(frozen=True)
class Activation:
    subject: Subject
    method: Method
    token: PortToken
    password: Password


@do(rollbackable.optionally)
def activate_by(
    do: Do,
    activation: Activation,
    request: HttpRequest,
) -> Optional[HttpResponse]:
    payload_of = adapters.payload_by(
        request,
        handling_of=do(adapters.endpoint_handler_of),
    )

    return cases.activate_by(
        _from_activation_to_access(activation),
        endpoint_of=do(adapters.endpoint_repository.get_of),
        payload_of=payload_of,
        close=adapters.endpoint_repository.close,
    )


def _from_activation_to_access(
    activation: Activation,
) -> adapters.AccessToEndpoint:
    port = adapters.Port(activation.subject, activation.method)

    return adapters.AccessToEndpoint(
        activation.token,
        port,
        activation.password,
    )
