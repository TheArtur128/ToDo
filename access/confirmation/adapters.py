from secrets import token_urlsafe
from urllib.parse import urljoin
from typing import TypeAlias, Callable, Optional, Generic, Final

from act import (
    will, via_indexer, partial, partially, obj, then, to, func, rwill, v, I,
    ActionT
)
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.http import HttpRequest, HttpResponse
from django.template.loader import render_to_string
from django.urls import reverse

from access.confirmation import core
from shared.adapters import CacheRepository
from shared.types_ import (
    Token, URL, Email, Password, ID, RepositoryFromTo, Annotaton
)


Subject: TypeAlias = str
Method: TypeAlias = str

Port: TypeAlias = core.Port[Subject, Method]
AccessToEndpoint: TypeAlias = core.AccessToEndpoint[Token, Port, Password]


@via_indexer
def EndpointOf(notification_resource_annotation: Annotaton) -> Annotaton:
    return core.Endpoint[
        Token, Port, notification_resource_annotation, Password
    ]


@via_indexer
def ViewHandlerOf(id_annotation: Annotaton) -> Annotaton:
    return Callable[[HttpRequest, id_annotation], Optional[HttpResponse]]


@partially
def handler_payload_of(
    handling_of: Callable[Port, ViewHandlerOf[I]],
    request: HttpRequest,
) -> Callable[EndpointOf[I], Callable[I, Optional[HttpResponse]]]:
    return func((v.port) |then>> handling_of |then>> rwill(partial)(request))


def confirmation_page_url_of(endpoint: EndpointOf[Email]) -> URL:
    args = [
        endpoint.port.subject,
        endpoint.port.notification_resource_type,
        endpoint.id,
    ]

    relative_url = reverse("access:confirm", args=args)

    return urljoin(settings.BASE_URL, relative_url)


def send_confirmation_mail_by(
    endpoint: EndpointOf[Email],
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
        recipient_list=[endpoint.id],
        fail_silently=True,
    )


password_hashes_of = will(CacheRepository)(
    salt="passwordhash", location=settings.PORTS_CACHE_LOCATION
)

ids_of = will(CacheRepository)(
    salt='ids', location=settings.PORTS_CACHE_LOCATION
)


@obj.of
class endpoint_repository:
    def get_of(access: AccessToEndpoint) -> Optional[EndpointOf[ID]]:
        password_hash_config = password_hashes_of(access.port.subject)
        password_hash = password_hash_config[access.endpoint_id]

        id_config = ids_of(access.port.notification_resource_type)
        target_id = id_config[access.endpoint_id]

        if password_hash is None or target_id is None:
            return None

        endpoint = core.Endpoint(
            access.endpoint_id,
            access.port,
            target_id,
            access.password,
        )

        return endpoint

    def save(endpoint: EndpointOf[ID]) -> None:
        password_hash_config = password_hashes_of(endpoint.port.subject)
        password_hash_config[endpoint.id] = make_password(endpoint.password)

        id_config = ids_of(endpoint.port.notification_resource_type)
        id_config[endpoint.id] = endpoint.notification_resource

    def close(endpoint: EndpointOf[ID]) -> None:
        del password_hashes_of(endpoint.port.subject)[endpoint.id]
        del ids_of(endpoint.port.notification_resource_type)[endpoint.id]


class _EndpointHandlerRepositoryOfConfig(Generic[ActionT]):
    __ConfigRepository = RepositoryFromTo[Port, dict[Method, ActionT]]

    def __init__(self, config_repository: __ConfigRepository) -> None:
        self.__config_repository = config_repository

    def get_of(self, port: Port) -> ActionT:
        config = self.__config_repository.get_of(port)

        return config[port.notification_resource_type]

    def registrate_for(self, port: Port, handler: ActionT) -> None:
        if not self.__config_repository.has_of(port):
            self.__config_repository.create_for(port)

        config = self.__config_repository.get_of(port)
        config[port.notification_resource_type] = handler


@obj.of
class _django_config_repository:
    _HANDLERS_FIELD_NAME: Final[str] = "_HANDLERS"

    def get_of(port: Port) -> dict[Method, ViewHandlerOf[I]]:
        handler_configs = settings.PORTS[port.subject]
        handlers = (
            handler_configs[_django_config_repository._HANDLERS_FIELD_NAME]
        )

        return handlers[port.notification_resource_type]

    def has_of(port: Port) -> bool:
        field_names = settings.PORTS[port.subject].keys()

        return _django_config_repository._HANDLERS_FIELD_NAME in field_names

    def create_for(port: Port) -> None:
        config = settings.PORTS[port.subject]
        config[_django_config_repository._HANDLERS_FIELD_NAME] = dict()


endpoint_handler_repository = _EndpointHandlerRepositoryOfConfig(
    _django_config_repository
)

view_handler_payload_of = handler_payload_of(endpoint_handler_repository.get_of)

generate_endpoint_password = (
    token_urlsafe |to| settings.PORT_ENDPOINT_PASSWORD_LENGTH
)

generate_endpoint_token = (
    token_urlsafe |to| settings.PORT_ENDPOINT_TOKEN_LENGTH
)
