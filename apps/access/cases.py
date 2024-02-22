from typing import Callable, Any, Optional

from act import val, raise_

from apps.access import errors, rules
from apps.access.sugar import latest, exists, to_raise_multiple_errors
from apps.access.types_ import Username, Email, Password, PasswordHash, URL


@val
class registration:
    @to_raise_multiple_errors
    def open_using(
        name=Username,
        email=Email,
        password=Password,
        repeated_password=Password,
        *,
        is_there_user_named: Callable[Username, bool],
        is_there_user_with_email: Callable[Email, bool],
        confirmation_page_url_of: Callable[Email, Optional[URL]],
        hash_of: Callable[Password, PasswordHash],
        remember: Callable[rules.User, Any],
    ) -> URL:
        user = rules.AuthenticationUser(name, email, password)
        yield from rules.authentication_users.is_valid(user)
        yield from rules.passwords.is_remembered(password, repeated_password)

        if is_there_user_named(name):
            yield errors.UsernameExists()

        if is_there_user_with_email(email):
            yield errors.UserEmailExists()

        yield raise_

        confirmation_page_url = confirmation_page_url_of(email)
        yield from exists(confirmation_page_url, errors.EmailConfirmation())
        yield raise_

        remember(rules.User(user.name, user.email, hash_of(user.password)))

        return confirmation_page_url

    @to_raise_multiple_errors
    def complete_by[UserT: rules.User](
        email: Email,
        *,
        remembered_user_of: Callable[Email, Optional[UserT]],
        forgotten: Callable[UserT, Any],
        is_there_user_named: Callable[Username, bool],
        is_there_user_with_email: Callable[Email, bool],
        saved: Callable[UserT, Any],
        authorized: Callable[UserT, Any],
    ) -> UserT:
        user = remembered_user_of(email)
        yield from exists(user, errors.NoUser())

        if is_there_user_named(user.name):
            yield errors.UsernameExists()

        if is_there_user_with_email(email):
            yield errors.UserEmailExists()

        yield raise_

        return authorized(saved(forgotten(user)))


@val
class authorization:
    @to_raise_multiple_errors
    def open_using[UserT: rules.User](
        name: Username,
        password: Password,
        *,
        user_of: Callable[Username, Optional[UserT]],
        is_hash_of: Callable[[Password, PasswordHash], bool],
        confirmation_page_url_of: Callable[UserT, Optional[URL]],
    ) -> URL:
        user = user_of(name)
        yield from exists(user, errors.NoUser())

        if not is_hash_of(password, user.password_hash):
            yield errors.PasswordMismatch()

        yield raise_

        confirmation_page_url_of = confirmation_page_url_of(user)
        yield from exists(confirmation_page_url_of, errors.Confirmation())

        return confirmation_page_url_of

    @to_raise_multiple_errors
    def complete_by[UserT: rules.User, AuthorizedT: rules.User](
        email: Email,
        *,
        user_of: Callable[Email, Optional[UserT]],
        authorized: Callable[UserT, AuthorizedT],
    ) -> AuthorizedT:
        user = user_of(email)
        yield from exists(user, errors.NoUser())

        yield raise_

        return authorized(user)


@val
class access_recovery:
    @to_raise_multiple_errors
    def open_using[ID: Email | Username, UserT: rules.User](
        id: ID,
        new_password: Password,
        repeated_password: Password,
        *,
        user_of: Callable[ID, Optional[UserT]],
        confirmation_page_url_of: Callable[UserT, Optional[URL]],
        hash_of: Callable[Password, PasswordHash],
        remember_under: Callable[[Email, PasswordHash], Any],
    ) -> URL:
        user = user_of(id)
        yield from exists(user, errors.NoUser())
        yield from (
            rules.passwords.is_remembered(new_password, repeated_password)
        )

        yield raise_

        confirmation_page_url = confirmation_page_url_of(user)
        yield from latest(exists(confirmation_page_url, errors.Confirmation()))

        remember_under(user.email, hash_of(new_password))

        return confirmation_page_url

    @to_raise_multiple_errors
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
        user = user_of(email)
        yield from exists(user, errors.NoUser())
        yield raise_

        password_hash = remebered_password_hash_of(user.email)
        yield from latest(exists(password_hash, errors.NoPassword()))

        forget_password_hash_under(user.email)

        user.password_hash = password_hash

        return authorized(updated(user))
