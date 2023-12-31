from typing import Optional

from act import type, val, obj, do, Do, optionally, contextual, saving_context
from django.contrib import auth
from django.contrib.auth.hashers import make_password
from django.http import HttpRequest
from django_redis import get_redis_connection
from redis import Redis

from apps.access import models, ui
from apps.access.types_ import URL, Email, Password, PasswordHash, Username
from apps.access.utils import confirmation, hashed, unhashed, ui as uilib


type User = models.User


@val
class _access:
    def registered(user: User) -> User:
        if _user_django_orm_repository.has(user):
            return user

        _user_django_orm_repository.save(user)

        return user

    def authorized(user: User, request: HttpRequest) -> User:
        auth.login(request, user)

        return user


@val
class _user_django_orm_repository:
    def save(user: User) -> None:
        user.set_password(user.password)
        user.save()

    def has(user: User) -> bool:
        return user.id is not None

    def get_by_email(email: Email) -> User:
        return models.User.objects.filter(email=email).first()

    def get_by_name(name: Username) -> User:
        return models.User.objects.filter(name=name).first()


@val
class registration:
    UserID = type(name=Username, email=Email, password=Password)

    def user_of(user_id: UserID) -> Optional[User]:
        user = models.User(
            name=user_id.name,
            email=user_id.email,
            password=user_id.password,
        )

        return None if _user_django_orm_repository.has(user) else user

    @obj
    class confirmation:
        @do(optionally)
        def add(do: Do, self, user: User) -> URL:
            confirmation_page_url = do(confirmation.open_port_of)(
                confirmation.subjects.registration,
                confirmation.via.email,
                for_=user.email,
            )

            self._user_repository.save(user)

            return confirmation_page_url

        @do(optionally)
        def pop_by(do: Do, self, email: Email) -> User:
            user = do(self._user_repository.get_by)(email)
            self._user_repository.delete(user)

            return user

        @obj
        class _user_repository:
            _connection: Redis = get_redis_connection("registration")
            _activity_seconds: int = confirmation.activity_minutes * 60

            def save(self, user: User) -> None:
                password_hash = hashed(user.password)

                self._connection.hset(user.email, "name", user.name)
                self._connection.hset(
                    user.email, "password_hash", password_hash
                )

                self._connection.expire(user.email, self._activity_seconds)

            @do(optionally)
            def get_by(do: Do, self, email: Email) -> User:
                name = do(self._connection.hget)(email, "name").decode()
                password_hash = do(self._connection.hget)(
                    email,
                    "password_hash",
                ).decode()

                password = unhashed(password_hash)

                return models.User(name=name, email=email, password=password)

            def delete(self, user: User) -> None:
                self._connection.hdel(user.email, "name", "password_hash")

    registered = _access.registered
    authorized = _access.authorized


@val
class authorization:
    UserID = type(name=Username, password=Password)

    def user_to_open_by(
        user_id: UserID,
        request: HttpRequest,
    ) -> Optional[User]:
        return auth.authenticate(
            request,
            username=user_id.name,
            password=user_id.password,
        )

    user_to_complate_by = _user_django_orm_repository.get_by_email

    def open_confirmation_for(user: User) -> URL:
        return confirmation.open_port_of(
            confirmation.subjects.authorization,
            confirmation.via.email,
            for_=user.email,
        )

    authorized = _access.authorized


@val
class access_recovery:
    @val
    class opening:
        type _UserID[ID] = contextual[Password, ID]
        type _User = contextual[Password, User]

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
        authorized = _access.authorized

        @do(optionally)
        def with_new_password(do, user: User) -> User:
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
    def user_of(user: User) -> User:
        return user

    def profile_of(user: User) -> uilib.LazyPage:
        return ui.profile.page_of(user)
