from typing import Optional

from act import val, obj, do, Do, optionally
from django.contrib import auth
from django.http import HttpRequest
from django_redis import get_redis_connection
from redis import Redis

from apps.access import models
from apps.access.types_ import URL, Email
from apps.access.utils import confirmation, hashed, unhashed


type User = models.User


@val
class registration_confirmation:
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


def open_access_recovery_confirmation_for(user: User) -> URL:
    return confirmation.open_port_of(
        confirmation.subjects.access_recovery,
        confirmation.via.email,
        for_=user.email,
    )


def open_authorization_confirmation_for(user: User) -> URL:
    return confirmation.open_port_of(
        confirmation.subjects.authorization,
        confirmation.via.email,
        for_=user.email,
    )


def user_to_register_from(request: HttpRequest) -> Optional[User]:
    user = models.User(
        name=request.POST["name"],
        email=request.POST["email"],
        password=request.POST["password1"],
    )

    return None if user_django_orm_repository.has(user) else user


def user_to_authorize_from(request: HttpRequest) -> Optional[User]:
    return auth.authenticate(
        request,
        username=request.POST["username"],
        password=request.POST["password"],
    )


def registered(user: User) -> Optional[User]:
    if user_django_orm_repository.has(user):
        return None

    user_django_orm_repository.save()

    return user


def authorized(user: User, request: HttpRequest) -> User:
    auth.login(request, user)

    return user


@val
class user_django_orm_repository:
    def save(user: User) -> None:
        user.set_password(user.password)
        user.save()

    def has(user: User) -> bool:
        return user.id is not None

    def get_by_email(email: Email) -> User:
        return models.User.objects.filter(email=email).first()

    def get_by_name(name: str) -> User:
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
