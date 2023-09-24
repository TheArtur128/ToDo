from dataclasses import dataclass
from typing import TypeVar, Callable, Generic, Any

from act import via_indexer, temp, I, A, P, R, S, T, V

from shared.types_ import Annotaton


@dataclass(frozen=True)
class OpenedEndpoint(Generic[A, S]):
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
class EndpointActivation(Generic[A, S]):
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
