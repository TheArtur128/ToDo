from secrets import token_urlsafe

from django.core.cache import caches
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.urls import reverse


@partially
class _PortStorage(ABC):
    def __init__(self, subject: str, *, salt: str) -> None:
        self._subject = subject
        self._salt = salt

    def get_of(self, auth_token: str) -> str:
        return caches[settings.PORTS_CACHE_LOCATION].get(
            self.__key_for(auth_token)
        )

    def set_for(self, auth_token: str, value: str) -> str:
        caches[settings.PORTS_CACHE_LOCATION].set(
            self.__key_for(auth_token),
            value,
        )

    def delete(self, auth_token: str) -> str:
        caches[settings.PORTS_CACHE_LOCATION].delete(auth_token)

    def __key_for(self, *, auth_token: str) -> str:
        return f"{self._salt}:{self._subject}:{auth_token}"


port_password_hash_of = _PortStorage(salt='hash')
port_email_of = _PortStorage(salt='email')


def delete_of(auth_token: str, subject: str) -> None:
    port_password_hash_of(subject).delete(auth_token)
    port_email_of(subject).delete(auth_token)


def open_port_of(subject: str, *, for_: str) -> bool:
    email = for_

    auth_token = token_urlsafe(settings.PORT_AUTHENTICATION_TOKEN_LENGTH)
    password = token_urlsafe(settings.PORT_PASSWORD_LENGTH)
    password_hash = make_password(password)

    confirmation_page_url = urljoin(
        confirmation_page_url_of(subject), auth_token)

    ok = _send_confirmation_mail_to(
        email,
        subject_name=readable(subject),
        url=confirmation_page_url,
        password=password,
    )

    if ok:
        port_passwords_hash_of(subject).set_for(auth_token, password_hash)
        port_email_of(subject).set_for(auth_token, email)

    return ok


def confirmation_page_url_of(subject: str) -> str:
    return reverse(settings.PORTS[subject]["HANDLER"])


def readable(subject: str) -> str:
    return settings.PORTS[subject].get("READABLE", subject)


def _send_confirmation_mail_to(email: str, *, subject_name: str, url: str, password: str) -> bool:
    text_message = f"Password to confirm {subject_name} in {url}: {password}"
    html_message = render_to_string(
        "mails/to-confirm.html", dict(subject=subject_name, url=url, password=password))

    return 1 == send_mail(
        subject=f"Confirm {subject_name}",
        message=text_message,
        html_message=html_message,
        recipient_list=[email],
        fail_silently=True)
