from dataclasses import dataclass
from typing import TypeAlias, Optional

from django.http import HttpRequest, HttpResponse

from confirmation import adapters, core
from shared.types_ import Token, Password
from shared.transactions import do, rollbackable, Do


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
    return core.activate_by(
        _from_activation_to_access(activation),
        endpoint_of=do(endpoint_of_),
        payload_of=adapters.payload_by(request, handling_of=do(handling_of)),
        close=adapters.endpoint_repository.close,
    )


def _from_activation_to_access(
    activation: Activation,
) -> adapters.AccessToEndpoint:
    port = adapters.Port(activation.subject, activation.method)

    return adapters.AccessToEndpoint(activation.token, port, activation.password)
