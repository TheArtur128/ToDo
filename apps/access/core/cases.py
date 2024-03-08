from typing import Callable, Optional, Any

from act import val, raise_, struct

from apps.access.core import errors, rules
from apps.access.lib import last, latest, exists, to_raise_multiple_errors


type URL = str


@struct
class UserRepository:
    saved: Callable[rules.RegistrationUser, rules.User]
    has_named: Callable[rules.Username, bool]
    has_with_email: Callable[rules.Email, bool]
    get_by_email: Callable[rules.Email, Optional[rules.User]]
    get_by_name: Callable[rules.Email, Optional[rules.User]]
    committed: Callable[rules.User, rules.User]


@struct
class TemporaryUserRepository:
    saved: Callable[rules.RegistrationUser, rules.RegistrationUser]
    get_by: Callable[rules.Email, rules.RegistrationUser]
    deleted: Callable[rules.RegistrationUser, rules.RegistrationUser]


@struct
class TemporaryPasswordHashRepository:
    get_by: Callable[rules.Email, rules.PasswordHash]
    saved_under: Callable[[rules.Email, rules.PasswordHash], rules.PasswordHash]
    deleted: Callable[rules.Email, rules.Email]


@val
class registration:
    @struct
    class OpeningService:
        confirmation_page_url_of: Callable[rules.Email, Optional[URL]]
        hash_of: Callable[rules.Password, rules.PasswordHash]

    @struct
    class CompletionService:
        authorized: Callable[rules.User, rules.User]

    @struct
    class EventBus[ID: int]:
        send_user_is_registered: Callable[ID, Any]

    @to_raise_multiple_errors
    def open_using(
        name=rules.Username,
        email=rules.Email,
        password=rules.Password,
        repeated_password=rules.Password,
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
            yield errors.EmailExists()

        yield raise_

        confirmation_page_url = service.confirmation_page_url_of(email)
        yield from latest(exists(
            confirmation_page_url,
            errors.EmailConfirmation(),
        ))

        password_hash = service.hash_of(user.password)

        user = rules.RegistrationUser(user.name, user.email, password_hash)
        temporary_repo.saved(user)

        return confirmation_page_url

    @to_raise_multiple_errors
    def complete_by[UserT: rules.User](
        email: rules.Email,
        *,
        service: CompletionService,
        event_bus: EventBus,
        repo: UserRepository,
        temporary_repo: TemporaryUserRepository,
    ) -> UserT:
        user = temporary_repo.get_by(email)
        yield from exists(user, errors.NoUser())

        if repo.has_named(user.name):
            yield errors.UsernameExists()

        if repo.has_with_email(email):
            yield errors.EmailExists()

        yield raise_

        user = repo.saved(temporary_repo.deleted(user))
        event_bus.send_user_is_registered(user.id)

        return service.authorized(user)


@val
class authorization:
    @struct
    class OpeningService:
        is_hash_of: Callable[[rules.Password, rules.PasswordHash], bool]
        confirmation_page_url_of: Callable[rules.User, Optional[URL]]

    @struct
    class CompletionService:
        authorized: Callable[rules.User, rules.User]

    @to_raise_multiple_errors
    def open_using[UserT: rules.User](
        name: rules.Username,
        password: rules.Password,
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
        email: rules.Email,
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
        hash_of: Callable[rules.Password, rules.PasswordHash]
        confirmation_page_url_of: Callable[rules.User, Optional[URL]]
    
    @struct
    class CompletionService:
        authorized: Callable[rules.User, rules.User]

    type UserID = rules.Username | rules.Email

    @struct
    class UserRepository[ID: UserID]:
        user_of: Callable[ID, rules.User]

    @to_raise_multiple_errors
    def open_using[ID: UserID](
        id: ID,
        new_password: rules.Password,
        repeated_password: rules.Password,
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
        email: rules.Email,
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
