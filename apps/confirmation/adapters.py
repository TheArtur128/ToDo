from dataclasses import dataclass, field
from operator import setitem
from urllib.parse import urljoin
from typing import Callable, Optional

from act import (
    via_indexer, partial, obj, to, do, optionally, fun, I, Annotation
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
        input.tools.token_generator_with(length=input.session_code_length)
    ))


@dataclass(frozen=True)
class EndpointID:
    subject: Subject
    notification_method: Method
    session_code: SessionCode


def is_subject_correct(port: Port) -> bool:
    return port.subject in config.subjects.all


def is_method_correct(port: Port) -> bool:
    return port.notification_method in config.methods.all


def confirmation_page_url_of(
    endpoint: Endpoint[input.types_.Email],
) -> input.types_.URL:
    args = [
        endpoint.port.subject,
        endpoint.port.notification_method,
        endpoint.session_code,
    ]

    relative_url = reverse("confirmation:confirm", args=args)

    return urljoin(input.base_url, relative_url)


def send_confirmation_mail_by(
    endpoint: Endpoint[input.types_.Email],
    url: input.types_.URL,
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


@obj.of
class endpoint_repository:
    _seconds_until_deletion = input.activity_minutes * 60

    def _connect() -> Redis:
        return get_redis_connection("confirmation")

    @do(optionally)
    def get_of(do, id: EndpointID) -> Endpoint[str]:
        connection = endpoint_repository._connect()

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
        connection = endpoint_repository._connect()

        connection.hset(endpoint.session_code, "user_id", endpoint.user_id)
        connection.hset(
            endpoint.session_code,
            "activation_code",
            make_password(endpoint.activation_code),
        )

        seconds_until_deletion = endpoint_repository._seconds_until_deletion
        connection.expire(endpoint.session_code, seconds_until_deletion)

    def delete(endpoint: Endpoint[str]) -> None:
        connection = endpoint_repository._connect()
        connection.hdel(endpoint.session_code, "user_id", "activation_code")


@via_indexer
def HandlerOf(id_annotation: Annotation) -> Annotation:
    return Callable[[HttpRequest, id_annotation], Optional[HttpResponse]]


class handler_repository:
    _config: dict[Port, HandlerOf[I]] = dict()

    get_of = fun(_._config.get(e.port))
    save_for = setitem |to| _config


contextualized = partial

are_activation_codes_matched = check_password

generate_activation_code = input.tools.token_generator_with(
    length=input.activation_code_length,
)

