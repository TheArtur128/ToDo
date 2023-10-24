from typing import Callable, Optional

from act import obj, struct, contextual, U, A, M, D, I, S, F


@obj.of
class registration:
    @struct
    class Completion[A, F]:
        user_authorization: A
        user_forgetting: F

    def open_using(
        user_data: D,
        *,
        user_of: Callable[D, U],
        is_already_registered: Callable[U, bool],
        access_to_confirm_for: Callable[U, A],
        memorize: Callable[U, M],
    ) -> Optional[contextual[M, A]]:
        user = user_of(user_data)

        if is_already_registered(user):
            return None

        confirmation_access = access_to_confirm_for(user)
        memorization = memorize(user)

        return contextual(memorization, confirmation_access)

    def complete_by(
        user_id: I,
        *,
        memorized_user_of: Callable[I, U],
        forget: Callable[U, F],
        is_already_registered: Callable[U, bool],
        saved: Callable[U, S],
        authorize: Callable[S, A],
    ) -> Optional[Completion[A, F]]:
        user = memorized_user_of(user_id)
        user_forgetting = forget(user)

        if is_already_registered(user):
            return None

        user_authorization = authorize(saved(user))

        return registration.Completion(user_authorization, user_forgetting)


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
