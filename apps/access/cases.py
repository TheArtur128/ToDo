from typing import Callable, Any, Optional

from act import type, val, I, U, A, N, P

from apps.access import errors
from apps.access.types_ import Username, Email, Password, URL


User = type(name=Username, email=Email, password=Password)


@val
class registration:
    def open_using(
        name=Username,
        email=Email,
        password=Password,
        *,
        is_there_user_named: Callable[Username, bool],
        confirmation_page_url_of: Callable[Email, Optional[URL]],
        remember: Callable[User, Any],
    ) -> URL:
        if is_there_user_named(name):
            raise errors.UserExists()

        confirmation_page_url = confirmation_page_url_of(email)

        if confirmation_page_url is None:
            raise errors.EmailConfirmation()

        remember(User(name, email, password))

        return confirmation_page_url

    def complete_by[UserT: User](
        email: Email,
        *,
        remembered_user_of: Callable[Email, Optional[UserT]],
        is_there_user_named: Callable[Username, bool],
        forget: Callable[UserT, Any],
        save: Callable[UserT, Any],
        authorize: Callable[UserT, Any],
    ) -> UserT:
        user = remembered_user_of(email)

        if user is None:
            raise errors.NoUser()

        forget(user)

        if is_there_user_named(user.name):
            raise errors.UserExists()

        save(user)
        authorize(user)

        return user

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
        with_new_password: Callable[U, N],
        authorized: Callable[N, A],
    ) -> A:
        return authorized(with_new_password(user_of(user_id)))


@val
class profile:
    def of(
        user_id: I,
        *,
        user_of: Callable[I, U],
        profile_of: Callable[U, P],
    ) -> P:
        return profile_of(user_of(user_id))
