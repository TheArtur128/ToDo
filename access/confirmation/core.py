from typing import TypeAlias, Callable, Optional

from act import via_indexer, contextual, will, I, A, R

from core.types import Password


__all__ = (
    "Subject", "ReadableSubject", "AuthToken", "IdGroup", "id_groups",
    "subjects", "handler_of", "handle", "activate_by", "open_email_port_of"
)

Subject: TypeAlias = str
ReadableSubject: TypeAlias = str
AuthToken: TypeAlias = str
IdGroup: TypeAlias = str


@via_indexer
def HandlerRepositoryOf(handle_annotation: Annotaton) -> Annotaton
    return temp(
        registrate_for=Callable[PortID, reformer_of[handle_annotation]],
        get_of=Callable[PortID, handle_annotation],
    )


@via_indexer
def _AuthTokenSenderOf(
    id_annotation: Annotaton,
    access_token_annotation: Annotaton,
) -> Annotaton:
    return Callable[
        [id_annotation, ReadableSubject, access_token_annotation, Password],
        bool,
    ]


@dataclass(frozen=True)
class PortID(Generic[_IdGroupT]):
    subject: Subject
    id_group: IdGroup


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

    notify = will(notify_by)(PortView(id_, port_id.subject, access_token, password))

    create_port = will(create_port_from)(
        PortAccess(port_id=port_id, token=auth_token, password=password_hash),
        id_,
    )

    return transactionally_for(access_token)(notify, create_port)


def activate_by(
    access: PortAccess[Password],
    password_hash_of: Callable[[Subject, AuthToken], Optional[PasswordHash]],
    hash_equals: Callable[[Password, PasswordHash], bool],
    id_of: Callable[[IdGroup, AuthToken], I],
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

