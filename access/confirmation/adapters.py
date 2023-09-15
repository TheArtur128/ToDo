from urllib.parse import urljoin

from act import will
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.urls import reverse

from core.adapters import ChachRepository
from core.types import URL, Email, Password
from access.confirmation.core import PortID, AuthToken, Subject


def create_port(access: PortAccess[PasswordHash], id_: str) -> None:
    _password_hashes_of(access.port_id.subject)[access.token] = access.password
    _ids_that(access.port_id.id_group)[access.token] = id_


def close_port_of(identifier: PortID, token: AuthToken) -> None:
    del password_hashes_of(identifier.subject)[token]
    del ids_that(identifier.id_group)[token]


def send_confirmation_mail_to(view: PortAccessView[Email, URL]) -> bool:
    text_message = "Password to confirm {} in {}: {}".format(
        view.subject, view.access_token, view.password
    )

    context = dict(
        subject=view.subject, url=view.access_token, password=view.password
    )
    html_message = render_to_string("mails/to-confirm.html", context)

    return 1 == send_mail(
        subject=f"Confirm {view.subject}",
        message=text_message,
        html_message=html_message,
        recipient_list=[view.id_],
        fail_silently=True
    )


password_hashes_of = will(ChachRepository)(
    salt="passwordhash", location=settings.PORTS_CACHE_LOCATION
)

ids_that = will(ChachRepository)(
    salt='ids', location=settings.PORTS_CACHE_LOCATION
)


def confirmation_page_url_of(port_id: PortID, token: AuthToken) -> URL:
    relative_url = reverse(
        "access:confirm",
        args=[port_id.subject, port_id.id_group, token],
    )

    return urljoin(settings.BASE_URL, relative_url)
