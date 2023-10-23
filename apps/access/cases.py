from typing import Callable, Optional

from act import obj, struct, contextual, U, A, M, D, I, S


@obj.of
class registration:
    @struct
    class Completion[S, D]:
        user_saving: S
        memorization_deletion: D

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
        delete_memorization_of: Callable[U, D],
        is_already_registered: Callable[U, bool],
        authorized: Callable[U, A],
        save: Callable[A, S],
    ) -> Optional[Completion[S, D]]:
        user = memorized_user_of(user_id)
        memorization_deletion = delete_memorization_of(user)

        if is_already_registered(user):
            return None

        user_saving = save(authorized(user))

        return registration.Completion(user_saving, memorization_deletion)


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
