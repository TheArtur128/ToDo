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
    subject: Subject,
    *,
    for_: contextual[IdGroup, I],
    generate_auth_token: Callable[[], AuthToken],
    generate_password: Callable[[], Password],
    password_hash_of: Callable[Password, PasswordHash],
    access_token_of: Callable[[Subject, AuthToken], A],
    notify_by: Callable[PortAccessView[I, A], bool],
    create_port_from: Callable[[PortID, AuthToken, PasswordHash, I], bool],
) -> Optional[A]:
    id_group, id_ = for_

    auth_token = generate_auth_token()
    password = generate_password()
    password_hash = password_hash_of(password)

    access_token = access_token_of(subject, auth_token)

    notify = will(notify_by)(PortView(id_, port_id.subject, access_token, password))

    create_port = will(create_port_from)(
        PortID(subject, id_group), password_hash, id_
    )

    return transactionally_for(access_token)(notify, create_port)


def activate_by(
    access: PortAccess[Password],
    password_hash_of: Callable[[Subject, AuthToken], Optional[PasswordHash]],
    hash_equals: Callable[[Password, PasswordHash], bool],
    id_of: Callable[[IdGroup, AuthToken], I],
    handler_of: Callable[PortID, Callable[I, R]],
) -> Optional[R]:
    password_hash = password_hash_of(access.port_id.subject, access.token)
    is_password_correct = (
        password_hash is not None
        and hash_equals(access.password, password_hash)
    )

    if not is_password_correct:
        return None

    id_ = id_of(access.port_id.id_group, access.token)

    return handler_of(access.port_id)(id_)
