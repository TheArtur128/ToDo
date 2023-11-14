from typing import Callable

from act import val, U, A, I, R


@val
class registration:
    def open_using(
        user_id: I,
        *,
        user_of: Callable[I, U],
        access_to_confirm_for: Callable[U, A],
    ) -> A:
        return access_to_confirm_for(user_of(user_id))

    def complete_by(
        user_id: I,
        *,
        user_of: Callable[I, U],
        registered: Callable[U, R],
        authorized: Callable[R, A],
    ) -> A:
        return authorized(registered(user_of(user_id)))


@val
class authorization:
    def open_using(
        user_id: I,
        *,
        user_of: Callable[I, U],
        access_to_confirm_for: Callable[U, A],
    ) -> A:
        return access_to_confirm_for(user_of(user_id))

    def complete_by(
        user_id: I,
        *,
        user_of: Callable[I, U],
        authorized: Callable[U, A],
    ) -> A:
        return authorized(user_of(user_id))


@val
class access_recovery:
    def open_using(
        user_id: I,
        *,
        user_of: Callable[I, U],
        access_to_confirm_for: Callable[U, A],
    ) -> A:
        return access_to_confirm_for(user_of(user_id))

    def complete_by(
        user_id: I,
        *,
        user_of: Callable[I, U],
        with_restored_access: Callable[U, R],
        authorized: Callable[R, A],
    ) -> A:
        return authorized(with_restored_access(user_of(user_id)))
