from dataclasses import dataclass
from typing import Callable, Generic, Optional

from act import U, A, R, D, I, S


@dataclass(frozen=True)
class Registration(Generic[U, A]):
    access_to_confirm: A
    remembering_for_user: U


def registration_for(
    user: U,
    *,
    is_already_registered: Callable[U, bool],
    access_to_confirm_for: Callable[U, A],
    remembering_for: Callable[U, R],
) -> Optional[Registration[R, A]]:
    if is_already_registered(user):
        return None

    return Registration(access_to_confirm_for(user), remembering_for(user))


def register_by(
    user_id: I,
    *,
    remembered_user_by: Callable[I, U],
    is_already_registered: Callable[U, bool],
    authorized: Callable[U, A],
    saved: Callable[A, S],
) -> Optional[S]:
    user = remembered_user_by(user_id)

    return None if is_already_registered(user) else saved(authorized(user))


def authorization_by(
    user_data: D,
    *,
    user_by: Callable[D, U],
    open_port_for: Callable[U, A],
) -> A:
    user = user_by(user_data)

    access_to_confirm = open_port_for(user)

    return access_to_confirm


def access_recovery_by(
    user_id: I,
    *,
    user_by: Callable[I, U],
    open_port_for: Callable[U, A],
) -> A:
    user = user_by(user_id)

    access_to_confirm = open_port_for(user)

    return access_to_confirm


def authorize_by(
    user_id: I,
    *,
    user_by: Callable[I, U],
    authorized: Callable[U, A],
) -> A:
    return authorized(user_by(user_id))
