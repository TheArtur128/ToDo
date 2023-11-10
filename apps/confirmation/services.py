from typing import Optional

from act import (
    val, to, by, struct, io, do, Do, optionally, reformer_of, I
)
from django.http import HttpRequest, HttpResponse

from apps.confirmation import adapters, cases, input


type Subject = adapters.Subject
type Method = adapters.Method
type SessionToken = adapters.SessionCode


@struct
class _Sending[I]:
    method: adapters.Method
    __call__: adapters.Send[I]


@val
class sendings:
    email: _Sending[input.types_.Email] = val(
        method=adapters.methods.email,
        __call__=adapters.opening.send_activation_code_by.email,
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
    ) -> input.types_.URL:
        access_to_activate = (
            do(adapters.opening.access_to_activate) |by| sending.by
        )

        return cases.endpoint.open_by(
            adapters.opening.EndpointID(subject, sending.method, for_),
            endpoint_of=do(adapters.opening.endpoint_of),
            access_to_activate=access_to_activate,
        )

    do(optionally)
    def activate_by(
        do: Do,
        *,
        subject: Subject,
        method: Method,
        session_token: SessionToken,
        password: input.types_.Password,
        request: HttpRequest,
    ) -> Optional[HttpResponse]:
        id = adapters.activation.EndpointID(
            subject, method, session_token, password
        )

        return cases.endpoint.payload_by(
            id,
            do(adapters.activation.endpoint_of),
            do(adapters.activation.payload_of) |by| request,
        )

    def register_handler_for(
        subject: adapters.Subject,
        sending: _Sending[I],
    ) -> reformer_of[adapters.Handle[I]]:
        port = adapters.Port(subject, sending.method)
        registrate = adapters.handler_repository.save |to| port

        return io(registrate)
