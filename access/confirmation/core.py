from dataclasses import dataclass
from typing import TypeAlias, Callable, Optional, Generic, Any, Mapping

from act import will, temp, ActionT, I, A, P, R

from core.tools import transactionally_for
from core.types import Password, PasswordHash, Annotaton


__all__ = (
    "Subject", "AuthToken", "IDGroup", "PortID", "PortAccess", "PortAccessView",
    "open_port_of", "activate_by", "ConfigHandlerRepository"
)

Subject: TypeAlias = str
AuthToken: TypeAlias = str
IDGroup: TypeAlias = str


@dataclass(frozen=True)
class PortID:
    subject: Subject
    id_group: IDGroup


@dataclass(frozen=True)
class PortAccess(Generic[P]):
    port_id: PortID
    token: AuthToken
    password: P


@dataclass(frozen=True)
class PortAccessView(Generic[I, A]):
    id_: I
    subject: Subject
    access_token: A
    password: Password


def open_port_of(
    *,
    port_id: PortID,
    for_: I,
    generate_auth_token: Callable[[], AuthToken],
    generate_password: Callable[[], Password],
    password_hash_of: Callable[Password, PasswordHash],
    access_token_of: Callable[[PortID, AuthToken], A],
    notify_by: Callable[PortAccessView[I, A], bool],
    create_port_from: Callable[[PortAccess[PasswordHash], I], bool],
) -> Optional[A]:
    id_ = for_

    auth_token = generate_auth_token()
    password = generate_password()
    password_hash = password_hash_of(password)

    access_token = access_token_of(port_id, auth_token)

    notify = will(notify_by)(
        PortAccessView(id_, port_id.subject, access_token, password),
    )

    create_port = will(create_port_from)(
        PortAccess(port_id=port_id, token=auth_token, password=password_hash),
        id_,
    )

    return transactionally_for(access_token)(notify, create_port)


def activate_by(
    access: PortAccess[Password],
    password_hash_of: Callable[[Subject, AuthToken], Optional[PasswordHash]],
    hash_equals: Callable[[Password, PasswordHash], bool],
    id_of: Callable[[IDGroup, AuthToken], I],
    payload_of: Callable[PortID, Callable[I, P]],
    port_closing_by: Callable[[PortID, AuthToken], Callable[P, R]],
) -> Optional[R]:
    password_hash = password_hash_of(access.port_id.subject, access.token)
    is_password_correct = (
        password_hash is not None
        and hash_equals(access.password, password_hash)
    )

    if not is_password_correct:
        return None

    id_ = id_of(access.port_id.id_group, access.token)
    payload_result = payload_of(access.port_id)(id_)

    close_port_based_on = port_closing_by(access.port_id, access.token)

    return close_port_based_on(payload_result)


def _ConfigRepositoryOf(config_annotation: Annotaton) -> temp:
    return temp(
        get_of=Callable[PortID, config_annotation],
        has_of=Callable[PortID, bool],
        create_for=Callable[PortID, Any],
    )


class ConfigHandlerRepository(Generic[ActionT]):
    def __init__(
        self,
        config_repository: _ConfigRepositoryOf[Mapping[IDGroup, ActionT]],
    ) -> None:
        self.__config_repository = config_repository

    def get_of(self, port_id: PortID) -> ActionT:
        return self.__config_repository.get_of(port_id)[port_id.id_group]

    def registration_for(self, port_id: PortID, payload: ActionT) -> ActionT:
        if not self.__config_repository.has_of(port_id):
            self.__config_repository.create_for(port_id)

        config = self.__config_repository.get_of(port_id)
        config[port_id.id_group] = payload

        return payload
