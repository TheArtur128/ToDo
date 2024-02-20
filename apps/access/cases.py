from typing import Callable, Any, Optional

from act import val

from apps.access import errors, rules
from apps.access.sugar import same, valid
from apps.access.types_ import Username, Email, Password, PasswordHash, URL


@val
class registration:
    def open_using(
        name=Username,
        email=Email,
        password=Password,
        *,
        is_there_user_named: Callable[Username, bool],
        confirmation_page_url_of: Callable[Email, Optional[URL]],
        hash_of: Callable[Password, PasswordHash],
        remember: Callable[rules.User, Any],
    ) -> URL:
        if is_there_user_named(name):
            raise errors.UserExists()

        user = valid(
            rules.AuthenticationUser(name, email, password),
            rules.authentication_users.validate,
        )

        confirmation_page_url = same(
            confirmation_page_url_of(email), else_=errors.EmailConfirmation()
        )

        remember(rules.User(user.name, user.email, hash_of(user.password)))

        return confirmation_page_url

    def complete_by[UserT: rules.User](
        email: Email,
        *,
        remembered_user_of: Callable[Email, Optional[UserT]],
        forgotten: Callable[UserT, Any],
        is_there_user_named: Callable[Username, bool],
        saved: Callable[UserT, Any],
        authorized: Callable[UserT, Any],
    ) -> UserT:
        user = same(remembered_user_of(email), else_=errors.NoUser()) 
        user = forgotten(valid(user, rules.users.validate))

        if is_there_user_named(user.name):
            raise errors.UserExists()

        return authorized(saved(user))


@val
class authorization:
    def open_using[UserT: rules.User](
        name: Username,
        password: Password,
        *,
        user_of: Callable[Username, Optional[UserT]],
        is_hash_of: Callable[[Password, PasswordHash], bool],
        confirmation_page_url_of: Callable[UserT, Optional[URL]],
    ) -> URL:
        user = same(user_of(name), else_=errors.NoUser())
        user = valid(user, rules.users.validate)

        if not is_hash_of(password, user.password_hash):
            raise errors.PasswordMismatch()

        return same(confirmation_page_url_of(user), else_=errors.Confirmation())

    def complete_by[UserT: rules.User, AuthorizedT: rules.User](
        email: Email,
        *,
        user_of: Callable[Email, Optional[UserT]],
        authorized: Callable[UserT, AuthorizedT],
    ) -> AuthorizedT:
        user = same(user_of(email), else_=errors.NoUser())
        user = valid(user, rules.users.validate)

        return authorized(user)


@val
class access_recovery:
    def open_using[ID: Email | Username, UserT: rules.User](
        id: ID,
        new_password: Password,
        *,
        user_of: Callable[ID, Optional[UserT]],
        confirmation_page_url_of: Callable[UserT, Optional[URL]],
        hash_of: Callable[Password, PasswordHash],
        remember_under: Callable[[Email, PasswordHash], Any],
    ) -> URL:
        user = same(user_of(id), else_=errors.NoUser())
        user = valid(user, rules.users.validate)

        confirmation_page_url = (
            same(confirmation_page_url_of(user), else_=errors.Confirmation())
        )

        remember_under(user.email, hash_of(new_password))

        return confirmation_page_url

    def complete_by[
        UserT: rules.User, UpdatedT: rules.User, AuthorizedT: rules.User
    ](
        email: Email,
        *,
        user_of: Callable[Email, UserT],
        remebered_password_hash_of: Callable[Email, Optional[PasswordHash]],
        forget_password_hash_under: Callable[Email, Any],
        updated: Callable[UserT, UpdatedT],
        authorized: Callable[UpdatedT, AuthorizedT],
    ) -> UserT:
        user = same(user_of(email), else_=errors.NoUser())
        user = valid(user, rules.users.validate)

        password_hash = same(
            remebered_password_hash_of(user.email), else_=errors.NoPassword()
        )
        forget_password_hash_under(user.email)

        user.password_hash = password_hash

        return authorized(updated(user))
