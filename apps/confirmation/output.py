from typing import Callable, Any

from act import (
    to, via_indexer, temp, obj, io, will, rollbackable, do, Do, reformer_of, I,
    Annotation
)

from apps.confirmation import adapters, cases, config, input, views


__all__ = ("subjects", "via", "register_for", "open_port_of", "OpeningView")


subjects = config.subjects


@via_indexer
def _SendingOf(id_annotation: Annotation) -> temp:
    return temp(
        method=adapters.Method,
        by=Callable[
            adapters.Endpoint[id_annotation],
            Callable[input.types_.URL, Any],
        ],
    )


@obj.of
class via:
    email: _SendingOf[input.types_.Email] = obj(
        method=config.methods.email,
        by=will(rollbackable.binary(adapters.send_confirmation_mail_by)),
    )


def register_for(
    subject: adapters.Subject,
    send: _SendingOf[I],
) -> reformer_of[adapters.HandlerOf[I]]:
    port = adapters.Port(subject, send.method)
    registrate = adapters.handler_repository.save_for |to| port

    return io(registrate)


@do(else_=None)
def open_port_of(
    do: Do,
    subject: adapters.Subject,
    send: _SendingOf[I],
    *,
    for_: I,
) -> input.types_.URL:
    confirmation_page_url = cases.endpoint.open_for(
        adapters.Port(subject, send.method),
        for_,
        generate_activation_code=adapters.generate_activation_code,
        endpoint_for=adapters.Endpoint,
        place_to_activate=adapters.confirmation_page_url_of,
        sending_of=do(send.by),
        save=adapters.endpoint_repository.save,
    )

    return confirmation_page_url.value


OpeningView = views.OpeningView
