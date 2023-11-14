from typing import Optional, Callable

from act import val, obj, do, Do, optionally, contextual, saving_context
from django.contrib import auth
from django.contrib.auth.hashers import make_password
from django.http import HttpRequest
from django_redis import get_redis_connection
from redis import Redis

from apps.access import models
from apps.access.types_ import URL, Email, Password, PasswordHash, Username
from apps.access.utils import confirmation, hashed, unhashed


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


@obj
class _user_redis_repository:
    connection: Redis = get_redis_connection("registration")

    def save(self, user: User) -> None:
        password_hash = hashed(user.password)

        self.connection.hset(user.email, "name", user.name)
        self.connection.hset(user.email, "password_hash", password_hash)

        self.connection.expire(user.email, confirmation.activity_minutes * 60)

    @do(optionally)
    def get_by(do: Do, self, email: Email) -> User:
        name = do(self.connection.hget)(email, "name").decode()
        password_hash = do(self.connection.hget)(
            email,
            "password_hash",
        ).decode()

        password = unhashed(password_hash)

        return models.User(name=name, email=email, password=password)

    def delete(self, user: User) -> None:
        self.connection.hdel(user.email, "name", "password_hash")


@val
class registration:
    def user_of(request: HttpRequest) -> Optional[User]:
        user = models.User(
            name=request.POST["name"],
            email=request.POST["email"],
            password=request.POST["password1"],
        )

        return None if _user_django_orm_repository.has(user) else user

    @val
    class confirmation:
        @do(optionally)
        def add(do: Do, user: User) -> URL:
            confirmation_page_url = do(confirmation.open_port_of)(
                confirmation.subjects.registration,
                confirmation.via.email,
                for_=user.email,
            )

            _user_redis_repository.save(user)

            return confirmation_page_url

        @do(optionally)
        def pop_by(do: Do, email: Email) -> User:
            user = do(_user_redis_repository.get_by)(email)
            _user_redis_repository.delete(user)

            return user

    registered = _access.registered
    authorized = _access.authorized


@val
class authorization:
    def user_to_open_by(request: HttpRequest) -> Optional[User]:
        return auth.authenticate(
            request,
            username=request.POST["username"],
            password=request.POST["password"],
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
        def with_restored_access(do, user: User) -> User:
            password_hash_of = do(access_recovery._password_repository.pop_by)
            password_hash = password_hash_of(user.email)

            user.password = password_hash
            user.save()

            return user

    @obj
    class _password_repository:
        connection: Redis = get_redis_connection("access_recovery")

        def save_under(self, email: Email, password: Password) -> None:
            self.connection.set(email, make_password(password))
            self.connection.expire(email, confirmation.activity_minutes * 60)

        @do(optionally)
        def pop_by(do, self, email: Email) -> PasswordHash:
            password_hash = do(self.connection.get)(email)
            self.connection.del_(email)

            return password_hash
