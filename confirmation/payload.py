from dataclasses import dataclass
from typing import TypeAlias, Optional

from django.http import HttpRequest, HttpResponse

from confirmation import adapters, core
from shared.types_ import Token, Password
from shared.transactions import Transaction, rollbackable


Subject: TypeAlias = adapters.Subject
Method: TypeAlias = adapters.Method
PortToken: TypeAlias = Token


@dataclass(frozen=True)
class Activation:
    subject: Subject
    method: Method
    token: PortToken
    password: Password


@transaction
def activate_by(
    activation: Activation,
    request: HttpRequest,
) -> Optional[HttpResponse]:
    do = transactionally(optionally.do, binary.do)

    handling_of = rollbackable.optionally(adapters.endpoint_handler_of)
    endpoint_of = rollbackable.optionally(
        adapters.endpoint_repository.endpoint_of,
    )

    with Transaction() as get_ok:
        result = core.activate_by(
            _from_activation_to_access(activation),
            endpoint_of=endpoint_of,
            payload_of=adapters.payload_by(request, handling_of=handling_of),
            close=adapters.endpoint_repository.close,
        )

    return result if get_ok() else None



def _from_activation_to_access(
    activation: Activation,
) -> adapters.AccessToEndpoint:
    port = adapters.Port(activation.subject, activation.method)

    return adapters.AccessToEndpoint(activation.token, port, activation.password)
