from dataclasses import dataclass, field
from operator import setitem
from urllib.parse import urljoin
from typing import Callable, Optional

from act import val, obj, to, do, optionally, binary, fun, I, Do
from act.cursors.static import p, _
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password, check_password
from django.http import HttpRequest, HttpResponse
from django.template.loader import render_to_string
from django.urls import reverse
from django_redis import get_redis_connection

from apps.confirmation import config, types_, ui, utils


type Subject = config.Subject
type Method = config.Method
type SessionCode = types_.Token
type ActivationCode = types_.Token
type ActivationPlace = types_.URL

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
        utils.token_generator_with(length=config.activation_code_length)
    ))
    session_code: SessionCode = field(default_factory=(
        utils.token_generator_with(length=config.session_code_length)
    ))


type Handle[I] = Callable[[HttpRequest, I], Optional[HttpResponse]]
type Send[I] = Callable[[Endpoint[I], ActivationPlace], bool]


@val
class opening:
    @dataclass(frozen=True)
    class EndpointID[I]:
        subject: Subject
        notification_method: Method
        user_id: I

    def endpoint_of(id: EndpointID[I]) -> Optional[Endpoint[I]]:
        is_valid = (
            id.subject in config.subjects.all
            and id.notification_method in config.methods.all
        )

        if not is_valid:
            return None

        return Endpoint(Port(id.subject, id.notification_method), id.user_id)

    @do(binary, else_=None)
    def access_to_activate(
        do: Do,
        endpoint: Endpoint[I],
        send_activation_code: Send[I],
    ) -> ActivationPlace:
        confirmation_page_url = opening._confirmation_page_url_of(endpoint)

        do(send_activation_code)(endpoint, confirmation_page_url)
        _endpoint_repository.save(endpoint)

        return confirmation_page_url

    def _confirmation_page_url_of(
        endpoint: Endpoint[types_.Email],
    ) -> ActivationPlace:
        args = [
            endpoint.port.subject,
            endpoint.port.notification_method,
            endpoint.session_code,
        ]

        relative_url = reverse("confirmation:confirm", args=args)

        return urljoin(config.base_url, relative_url)

    @val
    class send_activation_code_by:
        def email(
            endpoint: Endpoint[types_.Email],
            url: ActivationPlace,
        ) -> bool:
            context = dict(
                subject=endpoint.port.subject,
                url=url,
                password=endpoint.activation_code,
            )

            text_message_template = (
                "Password to confirm {subject} in {url}: {password}"
            )
            text_message = text_message_template.format(**context)

            html_message = render_to_string(
                "confirmation/mails/to-confirm.html",
                context | dict(activity_minutes=ui.activity_minutes),
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


@val
class activation:
    @dataclass(frozen=True)
    class EndpointID:
        subject: Subject
        notification_method: Method
        session_code: SessionCode
        activation_code: ActivationCode

    @do(optionally)
    def endpoint_of(do: Do, id: EndpointID) -> Endpoint[str]:
        endpoint_ = do(_endpoint_repository.get_by)(id)

        if not check_password(id.activation_code, endpoint_.activation_code):
            return None

        return endpoint_

    @do(optionally)
    def payload_of(
        do: Do,
        endpoint: Endpoint[str],
        request: HttpRequest,
    ) -> Optional[HttpResponse]:
        handle = do(handler_repository.get_by)(endpoint.port)

        return handle(request, endpoint.user_id)


@val
class handler_repository:
    _config: dict[Port, Handle[I]] = dict()

    get_by = fun(_._config.get(p))
    save = setitem |to| _config


@obj
class _endpoint_repository:
    _connection = get_redis_connection("confirmation")
    _seconds_until_deletion = config.activity_minutes * 60

    @do(optionally)
    def get_by(do, self, id: activation.EndpointID) -> Endpoint[str]:
        user_id_bytes = do(self._connection.hget)(id.session_code, "user_id")
        activation_code_bytes = do(self._connection.hget)(
            id.session_code,
            "activation_code",
        )

        user_id = user_id_bytes.decode()
        activation_code = activation_code_bytes.decode()

        port = Port(id.subject, id.notification_method)
        endpoint = Endpoint(port, user_id, activation_code, id.session_code)

        return endpoint

    def save(self, endpoint: Endpoint[str]) -> None:
        self._connection.hset(
            endpoint.session_code,
            "user_id",
            endpoint.user_id,
        )

        self._connection.hset(
            endpoint.session_code,
            "activation_code",
            make_password(endpoint.activation_code),
        )

        self._connection.expire(
            endpoint.session_code,
            self._seconds_until_deletion,
        )

    def delete(self, endpoint: Endpoint[str]) -> None:
        fileds = ("user_id", "activation_code")
        self._connection.hdel(endpoint.session_code, *fileds)
