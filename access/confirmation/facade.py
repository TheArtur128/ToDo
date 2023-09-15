from urllib.parse import urljoin
from typing import Optional

from act import contextual, will
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.urls import reverse

from core.adapters import ChachRepository
from core.types import Email, URL, Password
from access.confirmation.adapters import _send_confirmation_mail_to
from access.confirmation.core import PortID, AuthToken, Subject


HANDLER_REPOSITORY = ConfigHandlerRepository(django_config_repository)


def activate_by(
    access: PortAccess,
    request: HttpRequest,
) -> Optional[HttpRequest]:
    return activate_by(
        access,
        password_hash_of=_._password_hashes_of(a)[b],
        hash_equals=check_password,
        id_of=_._ids_that(a)[b],
        payload_of=HANDLER_REPOSITORY.get_of |then>> rwill(partial)(request),
        port_closing_by=will(for_effect)(close_port_of),
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
        port_id=PortID(subject=subject, id_group=method),
        for_=for_,
        generate_auth_token=generate_auth_token,
        generate_password=generate_password,
        password_hash_of=make_password,
        access_token_of=confirmation_page_url_of,
        notify_by=send_confirmation_mail_to,
        create_port_from=create_port,
    )


@name_enum_of
class id_groups:
    email: core.IDGroup


@name_enum_of
class subjects:
    authorization: Subject
    registration: Subject

    @name_enum_of
    class access_recovery:
        via_email: Subject
        via_name: Subject
