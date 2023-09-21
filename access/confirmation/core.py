from dataclasses import dataclass
from typing import TypeVar, TypeAlias, Callable, Optional, Generic, Mapping

from act import will, ActionT, I, A, P, R, S, T, J, H, C, X

from core.tools import transactionally_for
from core.types import RepositoryFromTo


@dataclass(frozen=True)
class PortID(Generic[S, I]):
    subject: S
    target_id_group: I


_PortIDT = TypeVar("_PortIDT", bound=PortID)


@dataclass(frozen=True)
class PortEndpointID(Generic[S, I]):
    subject: S
    target_id: I


_PortEndpointIDT = TypeVar("_PortEndpointIDT", bound=PortEndpointID)


@dataclass(frozen=True)
class PortAccess(Generic[_PortIDT, T, P]):
    port_id: _PortIDT
    token: T
    password: P


@dataclass(frozen=True)
class PortEndpointView(Generic[_PortEndpointIDT, A, P]):
    port_endpoint_id: _PortEndpointIDT
    activation_access: A
    password: P


class ConfigPayloadRepository(Generic[ActionT]):
    __ConfigRepository: TypeAlias = RepositoryFromTo[
        PortID[S, J], Mapping[J, ActionT],
    ]

    def __init__(self, config_repository: __ConfigRepository) -> None:
        self.__config_repository = config_repository

    def get_of(self, port_id: PortID[S, J]) -> ActionT:
        return self.__config_repository.get_of(port_id)[port_id.id_group]

    def registrate_for(
        self,
        port_id: PortID[S, J],
        payload: ActionT,
    ) -> None:
        if not self.__config_repository.has_of(port_id):
            self.__config_repository.create_for(port_id)

        config = self.__config_repository.get_of(port_id)
        config[port_id.id_group] = payload


def open_port_of(
    *,
    port_id: PortID[S, J],
    target_id: I,
    port_access_token: T,
    password: P,
    password_hash_of: Callable[P, H],
    activation_access_of: Callable[[PortID[S, J], T], A],
    notify_by: Callable[PortEndpointView[PortID[S, J], A, P], bool],
    open_port_endpoint_from: Callable[
        [PortAccess[PortID[S, J], T, H], I],
        bool,
    ],
) -> Optional[A]:
    password_hash = password_hash_of(password)
    activation_access = activation_access_of(port_id, port_access_token)

    port_access = PortAccess(port_id, port_access_token, password_hash)
    port_endpoint_view = PortEndpointView(
        PortEndpointID(port_id.subject, target_id),
        activation_access,
        password,
    )

    notify = will(notify_by)(port_endpoint_view)
    open_port_endpoint = will(open_port_endpoint_from)(port_access, target_id)

    return transactionally_for(activation_access)(notify, open_port_endpoint)


def activate_by(
    access: PortAccess[PortID[S, J], T, P],
    *,
    password_hash_of: Callable[[S, T], Optional[H]],
    hash_equals: Callable[[P, H], bool],
    target_id_of: Callable[[J, T], I],
    payload_of: Callable[PortID, Callable[I, X]],
    port_closing_by: Callable[[PortID, T], Callable[X, R]],
) -> Optional[R]:
    password_hash = password_hash_of(access.port_id.subject, access.token)
    is_password_correct = (
        password_hash is not None
        and hash_equals(access.password, password_hash)
    )

    if not is_password_correct:
        return None

    target_id = target_id_of(access.port_id.id_group, access.token)
    payload_result = payload_of(access.port_id)(target_id)

    close_port_based_on = port_closing_by(access.port_id, access.token)

    return close_port_based_on(payload_result)
