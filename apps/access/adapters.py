from typing import Optional

from act import (
    val, obj, do, Do, optionally, contextual, saving_context, io
)
from django.contrib import auth
from django.contrib.auth.hashers import make_password
from django.http import HttpRequest
from django_redis import get_redis_connection
from redis import Redis

from apps.access import cases, models, ui
from apps.access.types_ import URL, Email, Password, PasswordHash, Username
from apps.access.lib import (
    confirmation, created_user_of, hashed, unhashed, ui as uilib
)


@val
class _user_django_orm_repository:
    def save(user: models.User) -> None:
        user.set_password(user.password)

        user.default_settings.save()
        user.save()

    def has(user: cases.User) -> bool:
        return models.User.objects.filter(name=user.name).exists()

    def is_there_user_named(name: Username) -> bool:
        return models.User.objects.filter(name=name).exists()

    def get_by_email(email: Email) -> Optional[models.User]:
        return models.User.objects.filter(email=email).first()

    def get_by_name(name: Username) -> Optional[models.User]:
        return models.User.objects.filter(name=name).first()


@obj
class _user_redis_repository:
    _connection: Redis = get_redis_connection("accounts")
    _activity_seconds: int = confirmation.activity_minutes * 60

    def save(self, user: cases.User) -> None:
        password_hash = hashed(user.password)

        self._connection.hset(user.email, "name", user.name)
        self._connection.hset(
            user.email, "password_hash", password_hash
        )

        self._connection.expire(user.email, self._activity_seconds)

    @do(optionally)
    def get_by(do: Do, self, email: Email) -> Optional[cases.User]:
        name = do(self._connection.hget)(email, "name").decode()
        password_hash = do(self._connection.hget)(
            email,
            "password_hash",
        ).decode()

        password = unhashed(password_hash)

        return cases.User(name, email, password)

    def delete(self, user: cases.User) -> None:
        self._connection.hdel(user.email, "name", "password_hash")


def _authorize(user: models.User, request: HttpRequest) -> None:
    auth.login(request, user)


@val
class registration:
    def is_there_user_named(name: Username) -> bool:
        return _user_django_orm_repository.is_there_user_named(name)

    def confirmation_page_url_of(email: Email) -> Optional[URL]:
        return confirmation.open_port_of(
            confirmation.subjects.registration,
            confirmation.via.email,
            for_=email,
        )

    def remember(user: cases.User) -> None:
        _user_redis_repository.save(user)

    def remembered_user_of(email: Email) -> Optional[models.User]:
        user = _user_redis_repository.get_by(email)

        return created_user_of(user.name, user.email, user.password)

    def forget(user: models.User) -> None:
        _user_redis_repository.delete(user)

    def save(user: models.User) -> None:
        _user_django_orm_repository.save(user)

    authorize = _authorize


@val
class authorization:
    @val
    class opening:
        def user_of(
            name: Username,
            password: Password,
            request: HttpRequest,
        ) -> Optional[models.User]:
            return auth.authenticate(request, username=name, password=password)

        def confirmation_page_url_of(user: cases.User) -> Optional[URL]:
            return confirmation.open_port_of(
                confirmation.subjects.authorization,
                confirmation.via.email,
                for_=user.email,
            )

    @val
    class completing:
        user_of = _user_django_orm_repository.get_by_email
        authorize = _authorize


@val
class access_recovery:
    @val
    class opening:
        type _UserID[ID] = contextual[Password, ID]
        type _User = contextual[Password, models.User]

        @do(optionally)
        def get_user_by_email(do: Do, id: _UserID[Email]) -> _User:
            return saving_context(do(_user_django_orm_repository.get_by_email))(
                id,
            )

        @do(optionally)
        def get_user_by_name(do: Do, id: _UserID[Username]) -> _User:
            return saving_context(do(_user_django_orm_repository.get_by_name))(
                id,
            )

        @do(optionally)
        def confirmation_for(do: Do, user_to_open: _User) -> URL:
            new_password, user = user_to_open

            confirmation_page_url = do(confirmation.open_port_of)(
                confirmation.subjects.access_recovery,
                confirmation.via.email,
                for_=user.email,
            )

            access_recovery._password_repository.save_under(
                user.email,
                new_password,
            )

            return confirmation_page_url

    @val
    class completion:
        user_of = _user_django_orm_repository.get_by_email
        authorized = io(_authorize)

        @do(optionally)
        def with_new_password(do, user: models.User) -> models.User:
            password_hash_of = do(access_recovery._password_repository.pop_by)
            password_hash = password_hash_of(user.email)

            user.password = password_hash
            user.save()

            return user

    @obj
    class _password_repository:
        _connection: Redis = get_redis_connection("access_recovery")

        def save_under(self, email: Email, password: Password) -> None:
            self._connection.set(email, make_password(password))
            self._connection.expire(email, confirmation.activity_minutes * 60)

        @do(optionally)
        def pop_by(do, self, email: Email) -> PasswordHash:
            password_hash_bytes = do(self._connection.get)(email)
            self._connection.delete(email)

            return password_hash_bytes.decode()


@val
class profile:
    def user_of(user: models.User) -> models.User:
        return user

    def profile_of(user: models.User) -> uilib.LazyPage:
        return ui.profile.page_of(user)
