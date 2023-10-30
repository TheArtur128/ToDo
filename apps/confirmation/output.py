from typing import Callable, Optional

from act import (
    to, contextual, struct, obj, io, will, optionally, do, Do, reformer_of, I,
)

from apps.confirmation import adapters, cases, config, input, views


__all__ = ("subjects", "via", "register_for", "open_port_of", "OpeningView")


subjects = config.subjects
activity_minutes = input.activity_minutes


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
        method=config.methods.email,
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


OpeningView = views.OpeningView
