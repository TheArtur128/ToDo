from typing import Callable, Any, Optional

from act import type, val

from apps.access import errors
from apps.access.sugar import same
from apps.access.types_ import Username, Email, Password, PasswordHash, URL


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

        confirmation_page_url = same(
            confirmation_page_url_of(email), else_=errors.EmailConfirmation()
        )

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
        user = same(remembered_user_of(email), else_=errors.NoUser())
        forget(user)

        if is_there_user_named(user.name):
            raise errors.UserExists()

        save(user)
        authorize(user)

        return user


@val
class authorization:
    def open_using[UserT: User](
        name: Username,
        password: Password,
        *,
        user_of: Callable[[Username, Password], Optional[UserT]],
        confirmation_page_url_of: Callable[UserT, Optional[URL]],
    ) -> URL:
        user = same(user_of(name, password), else_=errors.NoUser())
        return same(confirmation_page_url_of(user), else_=errors.Confirmation())

    def complete_by[UserT: User](
        email: Email,
        *,
        user_of: Callable[Email, Optional[UserT]],
        authorize: Callable[UserT, Any],
    ) -> UserT:
        user = same(user_of(email), else_=errors.NoUser())
        authorize(user)

        return user


@val
class access_recovery:
    def open_using[ID: Email | Username, UserT: User](
        id: ID,
        new_password: Password,
        *,
        user_of: Callable[ID, Optional[UserT]],
        confirmation_page_url_of: Callable[UserT, Optional[URL]],
        hash_of: Callable[Password, PasswordHash],
        remember_under: Callable[[Email, PasswordHash], Any],
    ) -> URL:
        user = same(user_of(id), else_=errors.NoUser())
        confirmation_page_url = (
            same(confirmation_page_url_of(user), else_=errors.Confirmation())
        )

        remember_under(user.email, hash_of(new_password))

        return confirmation_page_url

    def complete_by[UserT: User](
        email: Email,
        *,
        user_of: Callable[Email, UserT],
        remebered_password_hash_of: Callable[Email, Optional[PasswordHash]],
        forget_password_hash_under: Callable[Email, Any],
        authorize: Callable[UserT, Any],
    ) -> UserT:
        user = same(user_of(email), else_=errors.NoUser())

        password_hash = same(
            remebered_password_hash_of(user.email), else_=errors.NoPassword()
        )
        forget_password_hash_under(user.email)

        user.password = password_hash
        authorize(user)

        return user
