from dataclasses import dataclass
from typing import Callable, Generic

from act import U, A, R

from shared.tools import struct
from shared.types_ import Name, Email, Password


@dataclass(frozen=True)
class Registration(Generic[U, A]):
    access_to_confirm: A
    user_reminder: U


def registration_for(
    user: U,
    *,
    is_already_registered: Callable[U, bool],
    confirmation_access_for: Callable[U, A],
    reminder_of: Callable[U, R],
) -> Optional[Registration[R, A]]:
    if is_already_registered(user):
        return None

    return Registration(confirmation_access_for(user), reminder_of(user))


def register_user_by(
    user_id: I,
    *,
    remembered_user_by: Callable[I, U],
    is_already_registered: Callable[U, bool],
    authorized: Callable[U, A],
    saved: Callable[A, S],
) -> Optional[S]:
    user = remembered_user_by(user_id)

    return None if is_already_registered(user) else saved(authorized(user))


def authorize_user_by(
    user_id: I,
    *,
    user_by: Callable[I, U],
    authorized: Callable[U, A],
) -> A:
    return authorized(user_by(user_id))
