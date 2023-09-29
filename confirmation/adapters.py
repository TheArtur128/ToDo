from collections import defaultdict
from dataclasses import dataclass
from operators import getitem, setitem
from secrets import token_urlsafe
from urllib.parse import urljoin
from typing import TypeAlias, Callable, Optional, Generic

from act import will, via_indexer, partially, obj, then, to, func, v, I, N
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.http import HttpRequest, HttpResponse
from django.template.loader import render_to_string
from django.urls import reverse

from shared.adapters import CacheRepository
from shared.types_ import Token, URL, Email, Password, ID, Annotaton


Subject: TypeAlias = str
Method: TypeAlias = str


@dataclass(frozen=True, unsafe_hash=True)
class Port:
    subject: Subject
    notification_method: Method


@dataclass(frozen=True)
class AccessToEndpoint:
    endpoint_token: Token
    port: Port
    password: Password


@dataclass(frozen=True)
class Endpoint(Generic[N]):
    token: Token
    port: Port
    notification_resource: N
    password: Password


@via_indexer
def ViewHandlerOf(id_annotation: Annotaton) -> Annotaton:
    return Callable[[HttpRequest, id_annotation], Optional[HttpResponse]]


@partially
def payload_by(
    request: HttpRequest,
    endpoint: Endpoint[N],
    *,
    handling_of: Callable[Endpoint[N], ViewHandlerOf[N]],
) -> Optional[HttpResponse]:
    payload_of = handling_of(endpoint)

    return payload_of(request, endpoint.notification_resource)


def confirmation_page_url_of(endpoint: Endpoint[Email]) -> URL:
    args = [
        endpoint.port.subject,
        endpoint.port.notification_method,
        endpoint.token,
    ]

    relative_url = reverse("confirmation:confirm", args=args)

    return urljoin(settings.BASE_URL, relative_url)


def send_confirmation_mail_by(
    endpoint: Endpoint[Email],
    page_url: URL,
) -> bool:
    context = dict(
        subject=endpoint.port.subject,
        url=page_url,
        password=endpoint.password,
    )

    text_message_template = "Password to confirm {subject} in {url}: {password}"
    text_message = text_message_template.format(**context)

    html_message = render_to_string("mails/to-confirm.html", context)

    return 1 == send_mail(
        subject=f"Confirm {endpoint.port.subject}",
        message=text_message,
        html_message=html_message,
        recipient_list=[endpoint.token],
        fail_silently=True,
    )


password_hashes_of = will(CacheRepository)(
    salt="passwordhash", location=settings.CONFIRMATION_CACHE_LOCATION
)

ids_of = will(CacheRepository)(
    salt='ids', location=settings.CONFIRMATION_CACHE_LOCATION
)


@obj.of
class endpoint_repository:
    def get_of(access: AccessToEndpoint) -> Optional[Endpoint[ID]]:
        password_hash_config = password_hashes_of(access.port.subject)
        password_hash = password_hash_config[access.endpoint_token]

        id_config = ids_of(access.port.notification_method)
        target_id = id_config[access.endpoint_token]

        if password_hash is None or target_id is None:
            return None

        endpoint = Endpoint(
            access.endpoint_token,
            access.port,
            target_id,
            access.password,
        )

        return endpoint

    def save(endpoint: Endpoint[ID]) -> None:
        password_hash_config = password_hashes_of(endpoint.port.subject)
        password_hash_config[endpoint.token] = make_password(endpoint.password)

        id_config = ids_of(endpoint.port.notification_method)
        id_config[endpoint.token] = endpoint.notification_resource

    def close(endpoint: Endpoint[ID]) -> None:
        del password_hashes_of(endpoint.port.subject)[endpoint.token]
        del ids_of(endpoint.port.notification_method)[endpoint.token]


@obj.of
class local_endpoint_handler_repository:
    _config: defaultdict[Port, ViewHandlerOf[I]] = defaultdict()

    get_of = getitem |to| _config
    save_for = setitem |to| _config


endpoint_handler_of: Callable[Endpoint, Optional[ViewHandlerOf[I]]]
endpoint_handler_of = func(
    (v.port) |then>> local_endpoint_handler_repository.get_of
)

generate_endpoint_password = (
    token_urlsafe |to| settings.CONFIRMATION_ENDPOINT_PASSWORD_LENGTH
)

generate_endpoint_token = (
    token_urlsafe |to| settings.CONFIRMATION_ENDPOINT_TOKEN_LENGTH
)
