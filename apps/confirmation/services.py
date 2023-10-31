from typing import Optional, Callable

from act import (
    obj, will, to, contextual, struct, io, do, Do, optionally, reformer_of, I
)
from django.http import HttpRequest, HttpResponse

from apps.confirmation import adapters, cases
from apps.shared.types_ import Password


type Subject = adapters.Subject
type Method = adapters.Method
type SessionToken = adapters.SessionCode


@obj.of
class endpoint_activation_of:
    _can_endpoint_be_opened_of = will(cases.endpoint.can_be_opened_for)(
        is_subject_correct=adapters.is_subject_correct,
        is_method_correct=adapters.is_method_correct,
    )

    def __call__(
        subject: Subject,
        method: Method,
    ) -> Optional[Callable]:
        port = adapters.Port(subject, method)

        if not endpoint_activation_of._can_endpoint_be_opened_of(port):
            return None

        @do(optionally)
        def activate_endpoint_by(
            do: Do,
            session_token: SessionToken,
            password: Password,
            request: HttpRequest,
        ) -> HttpResponse:
            id = adapters.EndpointID(subject, method, session_token, password)

            result = do(cases.endpoint.activate_by)(
                id,
                endpoint_of=adapters.endpoint_of,
                is_activated=adapters.is_activated,
                payload_of=adapters.payload_of,
            )

            return result

        return activate_endpoint_by


@struct
class _Sending[I]:
    method: adapters.Method
    by: Callable[
        adapters.Endpoint[I],
        Optional[contextual[adapters.ActivationPlace, adapters.Endpoint[I]]],
    ]


@obj.of
class via:
    email: _Sending[input.types_.Email] = obj(
        method=adapters.methods.email,
        by=will(adapters.with_activation_method_sent_to_user)(
            send_activation_method_to_user=adapters.send_confirmation_mail_by,
        ),
    )


def register_for(
    subject: adapters.Subject,
    send: _Sending[I],
) -> reformer_of[adapters.HandlerOf[I]]:
    port = adapters.Port(subject, send.method)
    registrate = adapters.handler_repository.save |to| port

    return io(registrate)


@do(optionally)
def open_port_of(
    do: Do,
    subject: adapters.Subject,
    send: _Sending[I],
    *,
    for_: I,
) -> adapters.ActivationPlace:
    return cases.endpoint.open_for(
        adapters.Port(subject, send.method),
        for_,
        endpoint_of=adapters.Endpoint,
        with_activation_method_sent_to_user=do(send.by),
        place_to_activate=adapters.place_to_activate,
    )
