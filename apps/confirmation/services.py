from typing import Optional, Iterable, Any

from act import (
    val, to, by, struct, io, do, Do, optionally, reformer_of, I, bad
)
from django.http import HttpRequest, HttpResponse

from apps.confirmation import adapters, cases, types_


type Subject = adapters.Subject
type Method = adapters.Method
type SessionToken = adapters.SessionCode
type ActivationToken = adapters.ActivationToken


@struct
class _Sending[I]:
    method: adapters.Method
    __call__: adapters.Send[I]


@val
class sendings:
    email: _Sending[types_.Email] = val(
        method=adapters.methods.email,
        __call__=adapters.opening.send_activation_code_by.email,
    )
    console: _Sending[Any] = val(
        method=adapters.methods.console,
        __call__=adapters.opening.send_activation_code_by.console,
    )


@val
class endpoint:
    @do(optionally)
    def open_for(
        do: Do,
        subject: Subject,
        sending: _Sending[I],
        *,
        for_: I,
    ) -> types_.URL:
        access_to_activate = (
            do(adapters.opening.access_to_activate) |by| sending
        )

        return cases.endpoint.open_by(
            adapters.opening.EndpointID(subject, sending.method, for_),
            endpoint_of=do(adapters.opening.endpoint_of),
            access_to_activate=access_to_activate,
        )

    @do(optionally)
    def activate_by(
        do: Do,
        *,
        subject: Subject,
        method: Method,
        session_token: SessionToken,
        activation_token: ActivationToken,
        request: HttpRequest,
    ) -> Optional[HttpResponse | bad[Iterable[str]]]:
        id = adapters.activation.EndpointID(
            subject, method, session_token, activation_token
        )

        return cases.endpoint.activate_by(
            id,
            endpoint_of=do(adapters.activation.endpoint_of),
            payload_of=do(adapters.activation.payload_of) |by| request,
        )

    def register_handler_for(
        subject: adapters.Subject,
        sending: _Sending[I],
    ) -> reformer_of[adapters.Handle[I]]:
        port = adapters.Port(subject, sending.method)
        registrate = adapters.handler_repository.save |to| port

        return io(registrate)
