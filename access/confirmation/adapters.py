from urllib.parse import urljoin

from act import will
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.urls import reverse

from core.adapters import ChachRepository
from core.types import URL, Email, Password
from access.confirmation.core import PortID, AuthToken, Subject


def close_port_of(identifier: PortID, token: AuthToken) -> None:
    del password_hashes_of(identifier.subject)[token]
    del ids_that(identifier.id_group)[token]


def send_confirmation_mail_to(
    email: Email, *, subject_name: Subject, url: URL, password: Password
) -> bool:
    text_message = f"Password to confirm {subject_name} in {url}: {password}"
    html_message = render_to_string(
        "mails/to-confirm.html",
        dict(subject=subject_name, url=url, password=password),
    )

    return 1 == send_mail(
        subject=f"Confirm {subject_name}",
        message=text_message,
        html_message=html_message,
        recipient_list=[email],
        fail_silently=True
    )


password_hashes_of = will(ChachRepository)(
    salt="passwordhash", location=settings.PORTS_CACHE_LOCATION
)

ids_that = will(ChachRepository)(
    salt='ids', location=settings.PORTS_CACHE_LOCATION
)


def confirmation_page_url_of(port_id: PortID, *, token: AuthToken) -> URL:
    relative_url = reverse(
        "access:confirm",
        args=[port_id.subject, port_id.id_group, token],
    )

    return urljoin(settings.BASE_URL, relative_url)
