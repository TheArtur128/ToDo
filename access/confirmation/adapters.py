from urllib.parse import urljoin
from typing import Callable, Optional, Generic, Final

from act import will, via_indexer, obj, I
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.template.loader import render_to_string
from django.urls import reverse

from core.adapters import CacheRepository
from core.types import URL, Email, PasswordHash, Annotaton
from access.confirmation.core import (
    PortID, AuthToken, PortAccess, PortAccessView, IDGroup
)


password_hashes_of = will(CacheRepository)(
    salt="passwordhash", location=settings.PORTS_CACHE_LOCATION
)

ids_that = will(CacheRepository)(
    salt='ids', location=settings.PORTS_CACHE_LOCATION
)


def create_port(access: PortAccess[PasswordHash], id_: str) -> None:
    password_hashes_of(access.port_id.subject)[access.token] = access.password
    ids_that(access.port_id.id_group)[access.token] = id_


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


def confirmation_page_url_of(port_id: PortID, token: AuthToken) -> URL:
    relative_url = reverse(
        "access:confirm",
        args=[port_id.subject, port_id.id_group, token],
    )

    return urljoin(settings.BASE_URL, relative_url)


@via_indexer
def _ViewHandlerFrom(id_annotation: Annotaton) -> Annotaton:
    return Callable[[HttpRequest, id_annotation], Optional[HttpResponse]]


@obj.of
class django_config_repository(Generic[I]):
    _HANDLERS_FIELD_NAME: Final[str] = "_HANDLERS"

    def get_of(port_id: PortID) -> dict[IDGroup, _ViewHandlerFrom[I]]:
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
