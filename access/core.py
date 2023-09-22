from typing import Callable, Any

from shared.tools import struct
from shared.types_ import Name, Email, Password


@struct
class User:
    name: Name
    email: Email
    password: Password


def open_registration_port_for(
    user: User.T,
    *,
    already_have: Callable[User.T, bool],
    open_confirmation_port_for: Callable[User.T, A],
    remember: Callable[User.T, Any],
) -> Optional[A]:
    if already_have(user):
        return None

    access_to_confirm = open_confirmation_port_for(user)
    remember(user)

    return access_to_confirm


def registrate(
    user: User.T,
    *,
    already_have: Callable[User.T, bool],
    authorized: Callable[User.T, A],
    saved: Callable[A, S],
) -> S:
    return None if already_have(user) else saved(authorized(user))
