from dataclasses import dataclass
from typing import Callable, Generic

from act import U, A, R

from shared.tools import struct
from shared.types_ import Name, Email, Password


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
