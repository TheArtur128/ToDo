from dataclasses import dataclass, field
from operator import setitem
from secrets import token_urlsafe
from urllib.parse import urljoin
from typing import Callable, Optional

from act import (
    via_indexer, partial, obj, to, as_method, do, optionally, fun, I, Annotaton
)
from act.cursors.static import e, _
from django.core.cache import caches
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from django.http import HttpRequest, HttpResponse
from django.template.loader import render_to_string
from django.urls import reverse

from shared.types_ import Token, URL, Email


type Subject = str
type Method = str
type SessionCode = Token
type ActivationCode = Token


@dataclass(frozen=True)
class Port:
    subject: Subject
    notification_method: Method


@dataclass(frozen=True)
class Endpoint[I]:
    port: Port
    user_id: I
    activation_code: ActivationCode
    session_code: SessionCode = field(default_factory=(
        token_urlsafe |to| settings.CONFIRMATION_SESSION_CODE_LENGTH
    ))


@dataclass(frozen=True)
class EndpointView:
    subject: Subject
    notification_method: Method
    session_code: SessionCode


def _confirmation_page_url_of(endpoint: Endpoint[Email]) -> URL:
    args = [
        endpoint.port.subject,
        endpoint.port.notification_method,
        endpoint.session_code,
    ]

    relative_url = reverse("confirmation:confirm", args=args)

    return urljoin(settings.BASE_URL, relative_url)


def send_confirmation_mail_by(endpoint: Endpoint[Email]) -> bool:
    context = dict(
        subject=endpoint.port.subject,
        url=_confirmation_page_url_of(endpoint),
        password=endpoint.activation_code,
    )

    text_message_template = "Password to confirm {subject} in {url}: {password}"
    text_message = text_message_template.format(**context)

    html_message = render_to_string("mails/to-confirm.html", context)

    result_code = send_mail(
        subject=f"Confirm {endpoint.port.subject}",
        message=text_message,
        html_message=html_message,
        recipient_list=[endpoint.user_id],
        fail_silently=True,
    )

    return result_code == 1


@obj.of
class endpoint_repository:
    _cache = caches["confirmation"].raw_client

    @as_method
    @do(optionally)
    def get_of(do, self, view: EndpointView) -> Endpoint[str]:
        user_id = do(self._cache.hget)(view.session_code, "user_id")
        activation_code = do(self._cache.hget)(
            view.session_code,
            "activation_code",
        )

        port = Port(view.subject, view.notification_method)
        endpoint = Endpoint(port, user_id, view.session_code, activation_code)

        return endpoint

    @as_method
    def save(self, endpoint: Endpoint[str]) -> None:
        self._cache.hset(endpoint.session_code, "user_id", endpoint.user_id)
        self._cache.hset(
            endpoint.session_code,
            "activation_code",
            make_password(endpoint.activation_code),
        )

    @as_method
    def delete(self, endpoint: Endpoint[str]) -> None:
        self._cache.raw_command("HDEL", endpoint.session_code, "user_id")
        self._cache.raw_command(
            "HDEL",
            endpoint.session_code,
            "activation_code",
        )


@via_indexer
def HandlerOf(id_annotation: Annotaton) -> Annotaton:
    return Callable[[HttpRequest, id_annotation], Optional[HttpResponse]]


class handler_repository:
    _config: dict[Port, HandlerOf[I]] = dict()

    get_of = fun(_._config.get(e.port))
    save_for = setitem |to| _config


contextualized = partial

are_activation_codes_matched = check_password

generate_activation_code = (
    token_urlsafe |to| settings.CONFIRMATION_ACTIVATION_CODE_LENGTH
)
