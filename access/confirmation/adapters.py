from secrets import token_urlsafe
from urllib.parse import urljoin
from typing import TypeAlias, Callable, Optional, Generic, Final

from act import will, via_indexer, obj, to, I
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.template.loader import render_to_string
from django.urls import reverse

from core.adapters import CacheRepository
from core.types import URL, Email, PasswordHash, Password, Annotaton
from access.confirmation import core


Subject: TypeAlias = str
PortAccessToken: TypeAlias = str
IDGroup: TypeAlias = str

PortID: TypeAlias = core.PortID[Subject, IDGroup]
ViewPortAccess: TypeAlias = core.PortAccess[
    core.PortID,
    PortAccessToken,
    Password,
]
PortAccess: TypeAlias = core.PortAccess[
    core.PortID,
    PortAccessToken,
    PasswordHash,
]


@via_indexer
def PortEndpointIDOf(targed_id_annotation: Annotaton) -> Annotaton:
    return core.PortEndpointID[PortID, targed_id_annotation]


@via_indexer
def PortEndpointViewOf(targed_id_annotation: Annotaton) -> Annotaton:
    return core.PortEndpointView[
        PortEndpointIDOf[targed_id_annotation],
        URL,
        Password,
    ]


password_hashes_of = will(CacheRepository)(
    salt="passwordhash", location=settings.PORTS_CACHE_LOCATION
)

ids_that = will(CacheRepository)(
    salt='ids', location=settings.PORTS_CACHE_LOCATION
)


@obj.of
class PortEndpointRepository:
    def open(access: PortAccess, id_: str) -> None:
        password_hash_by_token = password_hashes_of(access.port_id.subject)
        password_hash_by_token[access.token] = access.password

        ids_that(access.port_id.id_group)[access.token] = id_

    def close(port_id: PortID, token: PortAccessToken) -> None:
        del password_hashes_of(port_id.subject)[token]
        del ids_that(port_id.id_group)[token]


def send_confirmation_mail_to(view: PortEndpointViewOf[Email]) -> bool:
    text_message = "Password to confirm {} in {}: {}".format(
        view.port_endpoint_id.subject, view.activation_access, view.password
    )

    context = dict(
        subject=view.port_endpoint_id.subject,
        url=view.activation_access,
        password=view.password,
    )
    html_message = render_to_string("mails/to-confirm.html", context)

    return 1 == send_mail(
        subject=f"Confirm {view.subject}",
        message=text_message,
        html_message=html_message,
        recipient_list=[view.id_],
        fail_silently=True,
    )


def confirmation_page_url_of(port_id: PortID, token: PortAccessToken) -> URL:
    relative_url = reverse(
        "access:confirm",
        args=[port_id.subject, port_id.id_group, token],
    )

    return urljoin(settings.BASE_URL, relative_url)


@via_indexer
def ViewPayloadOf(id_annotation: Annotaton) -> Annotaton:
    return Callable[[HttpRequest, id_annotation], Optional[HttpResponse]]


@obj.of
class django_config_repository(Generic[I]):
    _HANDLERS_FIELD_NAME: Final[str] = "_HANDLERS"

    def get_of(port_id: PortID) -> dict[IDGroup, ViewPayloadOf[I]]:
        handler_configs = settings.PORTS[port_id.subject]
        handlers = (
            handler_configs[django_config_repository._HANDLERS_FIELD_NAME]
        )

        return handlers[port_id.id_group]

    def has_of(port_id: PortID) -> bool:
        field_names = settings.PORTS[port_id.subject].keys()

        return django_config_repository._HANDLERS_FIELD_NAME in field_names

    def create_for(port_id: PortID) -> None:
        config = settings.PORTS[port_id.subject]
        config[django_config_repository._HANDLERS_FIELD_NAME] = dict()


payload_repository = core.ConfigPayloadRepository(django_config_repository)

generate_password = token_urlsafe |to| settings.PORT_PASSWORD_LENGTH
generate_port_access_token = (
    token_urlsafe |to| settings.PORT_ACCESS_TOKEN_LENGTH
)
