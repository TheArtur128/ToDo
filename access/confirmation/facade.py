from dataclasses import dataclass
from typing import TypeAlias, Optional

from act import _, a, b, then, will, rwill, partial, returnly, reformer_of, I
from django.contrib.auth.hashers import make_password, check_password
from django.http import HttpRequest, HttpResponse

from core.tools import name_enum_of, for_effect
from core.types import URL, Token, Password
from access.confirmation import adapters
from access.confirmation import core
from access.confirmation import dto


Subject: TypeAlias = str
Method: TypeAlias = str
ID: TypeAlias = str
PortToken: TypeAlias = Token


class Method:
    def notify


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
    payload_of = (
        adapters.payload_repository.get_of |then>> rwill(partial)(request)
    )

    return core.activate_by(
        _from_activation_to_access(activation),
        password_hash_of=_.adapters.password_hashes_of(a)[b],
        hash_equals=check_password,
        target_id_of=_.adapters._ids_that(a)[b],
        payload_of=payload_of,
        port_closing_by=will(for_effect)(adapters.PortEndpointRepository.close),
    )


def registrate_for(subject: Subject, method: Method) -> reformer_of[
    adapters.ViewPayloadOf[I]
]:
    port_id = core.PortID(subject, method)

    return returnly(will(adapters.payload_repository.registrate_for)(port_id))


def open_port_of(
    subject: Subject,
    *,
    for_: ID,
    method: Method,
) -> Optional[URL]:
    return core.open_port_of(
        port_id=dto.PortID(subject=subject, id_group=method),
        target_id=for_,
        port_access_token=adapters.generate_port_access_token(),
        password=adapters.generate_password(),
        generate_password=adapters.generate_password(),
        password_hash_of=make_password,
        activation_access_of=adapters.confirmation_page_url_of,
        notify_by=adapters.send_confirmation_mail_to,
        open_port_endpoint_from=adapters.PortEndpointRepository.open,
    )


@name_enum_of
class methods:
    email: Method


@name_enum_of
class subjects:
    authorization: Subject
    registration: Subject

    @name_enum_of
    class access_recovery:
        via_email: Subject
        via_name: Subject


def _from_activation_to_access(
    activation: Activation,
) -> adapters.ViewPortAccess:
    return dto.PortAccess(
        dto.PortID(activation.subject, activation.method),
        activation.token,
        activation.password,
    )
