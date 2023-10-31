from dataclasses import dataclass, field
from operator import setitem
from urllib.parse import urljoin
from typing import Callable, Optional

from act import (
    contextual, via_indexer, obj, to, do, optionally, binary, fun, I,
    Annotation, Do
)
from act.cursors.static import e, _
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password, check_password
from django.http import HttpRequest, HttpResponse
from django.template.loader import render_to_string
from django.urls import reverse
from django_redis import get_redis_connection
from redis import Redis

from apps.confirmation import config, input


type Subject = config.Subject
type Method = config.Method
type SessionCode = input.types_.Token
type ActivationCode = input.types_.Token
type ActivationPlace = input.types_.URL

methods = config.methods


@dataclass(frozen=True)
class Port:
    subject: Subject
    notification_method: Method


@dataclass(frozen=True)
class Endpoint[I]:
    port: Port
    user_id: I
    activation_code: ActivationCode = field(default_factory=(
        input.tools.token_generator_with(length=input.activation_code_length)
    ))
    session_code: SessionCode = field(default_factory=(
        input.tools.token_generator_with(length=input.session_code_length)
    ))


@dataclass(frozen=True)
class EndpointID:
    subject: Subject
    notification_method: Method
    session_code: SessionCode
    activation_code: ActivationCode


def is_subject_correct(port: Port) -> bool:
    return port.subject in config.subjects.all


def is_activation_method_correct(port: Port) -> bool:
    return port.notification_method in config.methods.all


def _confirmation_page_url_of(
    endpoint: Endpoint[input.types_.Email],
) -> ActivationPlace:
    args = [
        endpoint.port.subject,
        endpoint.port.notification_method,
        endpoint.session_code,
    ]

    relative_url = reverse("confirmation:confirm", args=args)

    return urljoin(input.base_url, relative_url)


def send_confirmation_mail_by(
    endpoint: Endpoint[input.types_.Email],
    url: ActivationPlace,
) -> bool:
    context = dict(
        subject=endpoint.port.subject,
        url=url,
        password=endpoint.activation_code,
    )

    text_message_template = "Password to confirm {subject} in {url}: {password}"
    text_message = text_message_template.format(**context)

    html_message = render_to_string(
        "confirmation/mails/to-confirm.html",
        context | dict(link=url),
    )

    result_code = send_mail(
        from_email=None,
        subject=f"Confirm {endpoint.port.subject}",
        message=text_message,
        html_message=html_message,
        recipient_list=[endpoint.user_id],
        fail_silently=True,
    )

    return result_code == 1


@do(binary, else_=None)
def with_activation_method_sent_to_user(
    do: Do,
    endpoint: Endpoint[I],
    send_activation_method_to_user: Callable[
        [Endpoint[I], ActivationPlace],
        bool,
    ],
) -> contextual[ActivationPlace, Endpoint[I]]:
    confirmation_page_url = _confirmation_page_url_of(endpoint)
    do(send_activation_method_to_user)(endpoint, confirmation_page_url)

    return contextual(confirmation_page_url, endpoint)


def place_to_activate(
    io_endpoint: contextual[ActivationPlace, Endpoint[str]]
) -> ActivationPlace:
    _endpoint_repository.save(io_endpoint.value)

    return io_endpoint.context


def endpoint_to_activate(
    id: EndpointID
) -> contextual[EndpointID, Endpoint[str]]:
    endpoint_ = _endpoint_repository.get_of(id)
    return contextual(id, endpoint_)

    if not check_password(id.activation_code, endpoint_.activation_code):
        return None

    return endpoint_


def is_activated(
    io_endpoint: contextual[EndpointID, Endpoint[str]]
) -> Optional[Endpoint[str]]:
    id, endpoint_ = io_endpoint

    if not check_password(id.activation_code, endpoint_.activation_code):
        return None

    return endpoint_


@do(optionally)
def payload_of(
    do: Do,
    endpoint: Endpoint[str],
    request: HttpRequest,
) -> Optional[HttpResponse]:
    handle = do(handler_repository.get_of)(endpoint.port)

    return handle(request, endpoint.user_id)


@obj.of
class _endpoint_repository:
    _seconds_until_deletion = input.activity_minutes * 60

    def _connect() -> Redis:
        return get_redis_connection("confirmation")

    @do(optionally)
    def get_of(do, id: EndpointID) -> Endpoint[str]:
        connection = _endpoint_repository._connect()

        user_id_bytes = do(connection.hget)(id.session_code, "user_id")
        activation_code_bytes = do(connection.hget)(
            id.session_code,
            "activation_code",
        )

        user_id = user_id_bytes.decode()
        activation_code = activation_code_bytes.decode()

        port = Port(id.subject, id.notification_method)
        endpoint = Endpoint(port, user_id, activation_code, id.session_code)

        return endpoint

    def save(endpoint: Endpoint[str]) -> None:
        connection = _endpoint_repository._connect()

        connection.hset(endpoint.session_code, "user_id", endpoint.user_id)
        connection.hset(
            endpoint.session_code,
            "activation_code",
            make_password(endpoint.activation_code),
        )

        seconds_until_deletion = _endpoint_repository._seconds_until_deletion
        connection.expire(endpoint.session_code, seconds_until_deletion)

    def delete(endpoint: Endpoint[str]) -> None:
        connection = _endpoint_repository._connect()
        connection.hdel(endpoint.session_code, "user_id", "activation_code")


@via_indexer
def HandlerOf(id_annotation: Annotation) -> Annotation:
    return Callable[[HttpRequest, id_annotation], Optional[HttpResponse]]


class handler_repository:
    _config: dict[Port, HandlerOf[I]] = dict()

    get_of = fun(_._config.get(e.port))
    save = setitem |to| _config
