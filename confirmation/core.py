from dataclasses import dataclass
from typing import TypeVar, Callable, Generic, Any

from act import via_indexer, temp, I, A, P, R, S, T, V

from shared.types_ import Annotaton


@dataclass(frozen=True)
class Port(Generic[S, T]):
    subject: S
    notification_resource_type: T


PortT = TypeVar("PortT", bound=Port)


@dataclass(frozen=True)
class Endpoint(Generic[I, PortT, R, P]):
    id: I
    port: PortT
    notification_resource: R
    password: P


EndpointT = TypeVar("EndpointT", bound=Endpoint)


@dataclass(frozen=True)
class AccessToEndpoint(Generic[I, PortT, P]):
    endpoint_id: I
    port: PortT
    password: P


AccessToEndpointT = TypeVar("AccessToEndpointT", bound=AccessToEndpoint)


def open(
    endpoint: Endpoint[I, Port[S, T], R, P],
    *,
    access_to: Callable[Endpoint[I, Port[S, T], R, P],  A],
    sending_by: Callable[Endpoint[I, Port[S, T], R, P], Callable[A, Any]],
    save: Callable[Endpoint[I, Port[S, T], R, P], Any],
) -> A:
    access_to_endpoint = access_to(endpoint)

    send = sending_by(endpoint)
    send(access_to_endpoint)

    save(endpoint)

    return access_to_endpoint


def activate_by(
    access: AccessToEndpointT,
    *,
    endpoint_of: Callable[AccessToEndpointT, Endpoint[I, Port[S, T], V, P]],
    handling_of: Callable[Endpoint[I, Port[S, T], V, P], Callable[V, R]],
    close: Callable[Endpoint[I, Port[S, T], V, P], Any],
) -> R:
    endpoint = endpoint_of(access)

    handled = handling_of(endpoint)
    result = handled(endpoint.notification_resource)

    close(endpoint)

    return result


@via_indexer
def PortHandlerRepositoryOf(handler_annotation: Annotaton) -> temp:
    return temp(
        get_of=Callable[Port, handler_annotation],
        registrate_for=Callable[[Port, handler_annotation], Any],
    )
