from dataclasses import dataclass
from typing import Callable, Generic

from act import I, A, R, S, V, E, N, C


@dataclass(frozen=True)
class OpenedEndpoint[A, S]:
    access_to: A
    saving: S


def opened(
    endpoint: E,
    *,
    access_to: Callable[E, A],
    sending_by: Callable[E, Callable[A, N]],
    saving_for: Callable[E, V],
) -> OpenedEndpoint[N, V]:
    sended = sending_by(endpoint)

    return OpenedEndpoint(sended(access_to(endpoint)), saving_for(endpoint))


@dataclass(frozen=True)
class EndpointActivation[R, C]:
    result: R
    closure: C


def activate_by(
    endpoint_id: I,
    *,
    endpoint_of: Callable[I, E],
    payload_of: Callable[E, R],
    close: Callable[E, C],
) -> EndpointActivation[R, C]:
    endpoint = endpoint_of(endpoint_id)

    return EndpointActivation(
        result=payload_of(endpoint),
        closure=close(endpoint),
    )
