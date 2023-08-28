from enum import Enum
from secrets import token_urlsafe
from urllib.parse import urljoin

from act import via_indexer
from django.core.cache import caches
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.urls import reverse

from core.adapters import ChachRepository
from core.types import URL, Email
from core.tools import name_enum_of


__all__ = (
    "Subject", "ReadableSubject", "AuthToken", "Password", "PasswordHash",
    "IdGroup", "id_groups", "subjects", "handler_of", "handle", "activate"
    "by_email_open_port_of"
)

Subject: TypeAlias: TypeAlias = str
ReadableSubject: TypeAlias = str
AuthToken: TypeAlias = str
Password = str
PasswordHash: TypeAlias = str
IdGroup: TypeAlias = str

_SubjectHandlerOf = via_indexer(
    lambda id_type: Callable[[HttpRequest, id_type], HttpResponse]
)

_AuthTokenSenderOf_ = via_indexer(
    lambda id_type: Callable[[id_type, ReadableSubject, URL, Password], bool],
)


@name_enum_of
class id_groups:
    email: str


@name_enum_of
class subjects:
    authorization: str
    registration: str


def handler_of(subject: Subject, *, for_: IdGroup) -> _SubjectHandlerOf[Any]:
    return settings.PORTS[subject]["HANDLERS"][for_]


@partially
def handle(
    subject: Subject, of: IdGroup, action: _SubjectHandlerOf[I]
) -> _SubjectHandlerOf[I]:
    id_group = of

    @wraps(action)
    def subject_handler(request: HttpRequest, id_: I) -> HttpRequest:
        result = action(request, id_)

        _close_port_of(subject, token=token, id_group=id_group)

        return result

    settings.PORTS[subject]["HANDLERS"][id_group] = subject_handler

    return action


def activate(
    subject: Subject, *, token: AuthToken, id_group: IdGroup, password: Password
) -> Optional[HttpRequest]:
    password_hash = ports._password_hashes_of(subject)[token]
    is_password_correct = (
        password_hash is not None
        and check_password(password, password_hash)
    )

    if not is_password_correct:
        return None

    id_ = id_that(id_group)[token]

    return ports.handler_of(subject)(request, id_)


def _open_port_of(
    subject: Subject,
    *,
    for_: contextual[IdGroup, I],
    notify: _AuthTokenSenderOf_[I],
) -> Optional[URL]:
    id_group, id_ = for_

    auth_token = token_urlsafe(settings.PORT_AUTHENTICATION_TOKEN_LENGTH)
    password = token_urlsafe(settings.PORT_PASSWORD_LENGTH)
    password_hash = make_password(password)

    confirmation_page_url = _confirmation_page_url_of(subject, token=auth_token)

    ok = notify(id_, _readable(subject), confirmation_page_url, password)

    if ok:
        _password_hashes_of(subject)[auth_token] = password_hash
        _ids_that(id_group)[auth_token] = id_

        return confirmation_page_url


def _close_port_of(
    subject: Subject, token: AuthToken, id_group: IdGroup
) -> None:
    del _password_hashes_of(subject)[token]
    del _ids_that(id_group)[token]


def _send_confirmation_mail_to(
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


by_email_open_port_of = partial(open_port_of, notify=_send_confirmation_mail_to)


_password_hashes_of = will(_ChachRepository)(
    salt="passwordhash", location=settings.PORTS_CACHE_LOCATION
)

_ids_that = will(_ChachRepository)(
    salt='ids', location=settings.PORTS_CACHE_LOCATION
)


def _readable(subject: Subject) -> ReadableSubject:
    return settings.PORTS[subject].get("READABLE", subject)


def _confirmation_page_url_of(
    subject: Subject, *, token: AuthToken, id_group: IdGroup
) -> URL:
    return f"{{}}?notified-via={id_group}".format(urljoin(
        settings.BASE_URL, reverse("access:confirm", args=[subject, token])
    ))
