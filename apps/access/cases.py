from typing import Callable, Optional

from act import obj, U, A, D, I, R


@obj.of
class registration:
    def open_using(
        user_data: D,
        *,
        user_of: Callable[D, U],
        is_registered: Callable[U, bool],
        access_to_confirm_for: Callable[U, A],
    ) -> Optional[A]:
        user = user_of(user_data)

        return None if is_registered(user) else access_to_confirm_for(user)

    def complete_by(
        user_id: I,
        *,
        user_of: Callable[I, U],
        is_registered: Callable[U, bool],
        registered: Callable[U, R],
        authorized: Callable[R | U, A],
    ) -> A:
        user = user_of(user_id)

        return authorized(user if is_registered(user) else registered(user))


@obj.of
class authorization:
    def open_using(
        user_data: D,
        *,
        user_of: Callable[D, U],
        access_to_confirm_for: Callable[U, A],
    ) -> A:
        return access_to_confirm_for(user_of(user_data))

    def complete_by(
        user_id: I,
        *,
        user_of: Callable[I, U],
        authorized: Callable[U, A],
    ) -> A:
        return authorized(user_of(user_id))


@obj.of
class access_recovery:
    def open_using(
        user_id: I,
        *,
        user_of: Callable[I, U],
        access_to_confirm_for: Callable[U, A],
    ) -> A:
        return access_to_confirm_for(user_of(user_id))
