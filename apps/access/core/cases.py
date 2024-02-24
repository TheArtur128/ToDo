from typing import Callable, Optional

from act import val, raise_, struct

from apps.access.core import errors, rules
from apps.access.core.types_ import Username, Email, Password, PasswordHash, URL
from apps.access.lib import last, latest, exists, to_raise_multiple_errors


@struct
class UserRepository:
    saved: Callable[rules.User, rules.User]
    has_named: Callable[Username, bool]
    has_with_email: Callable[Email, bool]
    get_by_email: Callable[Email, Optional[rules.User]]
    get_by_name: Callable[Email, Optional[rules.User]]
    committed: Callable[rules.User, rules.User]


@struct
class TemporaryUserRepository:
    saved: Callable[rules.User, rules.User]
    get_by: Callable[Email, rules.User]
    deleted: Callable[rules.User, rules.User]


@struct
class TemporaryPasswordHashRepository:
    get_by: Callable[Email, PasswordHash]
    saved_under: Callable[[Email, PasswordHash], PasswordHash]
    deleted: Callable[Email, Email]


@val
class registration:
    @struct
    class OpeningService:
        confirmation_page_url_of: Callable[Email, Optional[URL]]
        hash_of: Callable[Password, PasswordHash]

    @struct
    class CompletionService:
        authorized: Callable[rules.User, rules.User]

    @to_raise_multiple_errors
    def open_using(
        name=Username,
        email=Email,
        password=Password,
        repeated_password=Password,
        *,
        service: OpeningService,
        repo: UserRepository,
        temporary_repo: TemporaryUserRepository,
    ) -> URL:
        user = rules.AuthenticationUser(name, email, password)
        yield from rules.passwords.is_remembered(password, repeated_password)
        yield from rules.authentication_users.is_valid(user)

        if repo.has_named(name):
            yield errors.UsernameExists()

        if repo.has_with_email(email):
            yield errors.UserEmailExists()

        yield raise_

        confirmation_page_url = service.confirmation_page_url_of(email)
        yield from exists(confirmation_page_url, errors.EmailConfirmation())
        yield raise_

        user = rules.User(user.name, user.email, service.hash_of(user.password))
        temporary_repo.saved(user)

        return confirmation_page_url

    @to_raise_multiple_errors
    def complete_by[UserT: rules.User](
        email: Email,
        *,
        service: CompletionService,
        repo: UserRepository,
        temporary_repo: TemporaryUserRepository,
    ) -> UserT:
        user = temporary_repo.get_by(email)
        yield from exists(user, errors.NoUser())

        if repo.has_named(user.name):
            yield errors.UsernameExists()

        if repo.has_with_email(email):
            yield errors.UserEmailExists()

        yield raise_

        return service.authorized(repo.saved(temporary_repo.deleted(user)))


@val
class authorization:
    @struct
    class OpeningService:
        is_hash_of: Callable[[Password, PasswordHash], bool]
        confirmation_page_url_of: Callable[rules.User, Optional[URL]]

    @struct
    class CompletionService:
        authorized: Callable[rules.User, rules.User]

    @to_raise_multiple_errors
    def open_using[UserT: rules.User](
        name: Username,
        password: Password,
        *,
        service: OpeningService,
        repo: UserRepository,
    ) -> URL:
        user = repo.get_by_name(name)
        yield from latest(exists(user, errors.NoUser()))

        if not service.is_hash_of(password, user.password_hash):
            yield last(errors.IncorrectPassword())

        confirmation_page_url_of = service.confirmation_page_url_of(user)
        yield from exists(confirmation_page_url_of, errors.Confirmation())

        return confirmation_page_url_of

    @to_raise_multiple_errors
    def complete_by(
        email: Email,
        *,
        service: CompletionService,
        repo: UserRepository,
    ) -> rules.User:
        user = repo.get_by_email(email)
        yield from exists(user, errors.NoUser())

        yield raise_

        return service.authorized(user)


@val
class access_recovery:
    @struct
    class OpeningService:
        hash_of: Callable[Password, PasswordHash]
        confirmation_page_url_of: Callable[rules.User, Optional[URL]]
    
    @struct
    class CompletionService:
        authorized: Callable[rules.User, rules.User]

    type UserID = Username | Email

    @struct
    class UserRepository[ID: UserID]:
        user_of: Callable[ID, rules.User]

    @to_raise_multiple_errors
    def open_using[ID: UserID](
        id: ID,
        new_password: Password,
        repeated_password: Password,
        *,
        service: OpeningService,
        user_repo: UserRepository[ID],
        password_hash_repo: TemporaryPasswordHashRepository,
    ) -> URL:
        user = user_repo.user_of(id)
        yield from exists(user, errors.NoUser())
        yield from rules.passwords.is_valid(new_password)
        yield from (
            rules.passwords.is_remembered(new_password, repeated_password)
        )

        yield raise_

        confirmation_page_url = service.confirmation_page_url_of(user)
        yield from latest(exists(confirmation_page_url, errors.Confirmation()))

        password_hash_repo.saved_under(
            user.email,
            service.hash_of(new_password),
        )

        return confirmation_page_url

    @to_raise_multiple_errors
    def complete_by(
        email: Email,
        *,
        service: CompletionService,
        user_repo: UserRepository,
        password_hash_repo: TemporaryPasswordHashRepository,
    ) -> rules.User:
        user = user_repo.get_by_email(email)
        yield from latest(exists(user, errors.NoUser()))

        password_hash = password_hash_repo.get_by(user.email)
        yield from latest(exists(password_hash, errors.NoPasswordHash()))
        password_hash_repo.deleted(user.email)

        user.password_hash = password_hash

        return service.authorized(user_repo.committed(user))
