from typing import Optional
from secrets import token_urlsafe

from act import _, a, b, then, will, rwill, partial, to
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from django.http import HttpRequest

from core.tools import name_enum_of, for_effect
from core.types import URL
from access.confirmation import adapters
from access.confirmation import core


HANDLER_REPOSITORY = ConfigHandlerRepository(django_config_repository)


def activate_by(
    access: core.PortAccess,
    request: HttpRequest,
) -> Optional[HttpRequest]:
    return core.activate_by(
        access,
        password_hash_of=_.adapters.password_hashes_of(a)[b],
        hash_equals=check_password,
        id_of=_.adapters._ids_that(a)[b],
        payload_of=HANDLER_REPOSITORY.get_of |then>> rwill(partial)(request),
        port_closing_by=will(for_effect)(adapters.close_port_of),
    )


def open_port_of(
    subject: core.Subject,
    *,
    for_: str,
    method: core.IDGroup,
) -> Optional[URL]:
    generate_auth_token = token_urlsafe |to| settings.PORT_AUTH_TOKEN_LENGTH
    generate_password = token_urlsafe |to| settings.PORT_PASSWORD_LENGTH

    return core.open_port_of(
        port_id=core.PortID(subject=subject, id_group=method),
        for_=for_,
        generate_auth_token=generate_auth_token,
        generate_password=generate_password,
        password_hash_of=make_password,
        access_token_of=adapters.confirmation_page_url_of,
        notify_by=adapters.send_confirmation_mail_to,
        create_port_from=adapters.create_port,
    )


@name_enum_of
class id_groups:
    email: core.IDGroup


@name_enum_of
class subjects:
    authorization: core.Subject
    registration: core.Subject

    @name_enum_of
    class access_recovery:
        via_email: core.Subject
        via_name: core.Subject
