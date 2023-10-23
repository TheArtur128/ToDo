from typing import Callable, Optional

from act import obj, contextual, U, A, M, D, I, S


@obj.of
class registration:
    def open_using(
        user_data: D,
        *,
        user_of: Callable[D, U],
        is_already_registered: Callable[U, bool],
        access_to_confirm_for: Callable[U, A],
        memorization_of: Callable[U, M],
    ) -> Optional[contextual[M, A]]:
        user = user_of(user_data)

        if is_already_registered(user):
            return None

        confirmation_access = access_to_confirm_for(user)
        memorization = memorization_of(user)

        return contextual(memorization, confirmation_access)

    def complete_by(
        user_id: I,
        *,
        memorized_user_of: Callable[I, U],
        is_already_registered: Callable[U, bool],
        authorized: Callable[U, A],
        saving_for: Callable[A, S],
    ) -> Optional[S]:
        user = memorized_user_of(user_id)

        if is_already_registered(user):
            return None

        return saving_for(authorized(user))


@obj.of
class authorization:
    def open_using(
        user_data: D,
        *,
        user_of: Callable[D, U],
        access_to_confirm_for: Callable[U, A],
    ) -> A:
        user = user_of(user_data)

        return access_to_confirm_for(user)

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
        user = user_of(user_id)

        return access_to_confirm_for(user)
