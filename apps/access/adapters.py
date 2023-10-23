from typing import Optional

from act import obj, flipped, io, fun, do, Do, optionally
from act.cursors.static import u, e, n, _
from django.contrib import auth
from django.http import HttpRequest
from django_redis import get_redis_connection
from redis import Redis

from apps.access.input import confirmation, models, types_, hashing


type User = models.User


def open_registration_confirmation_for(user: User) -> types_.URL:
    return confirmation.open_port_of(
        confirmation.subjects.registration,
        confirmation.via.email,
        for_=user.email,
    )


def open_access_recovery_confirmation_for(user: User) -> types_.URL:
    return confirmation.open_port_of(
        confirmation.subjects.access_recovery,
        confirmation.via.email,
        for_=user.email,
    )


def open_authorization_confirmation_for(user: User) -> types_.URL:
    return confirmation.open_port_of(
        confirmation.subjects.authorization,
        confirmation.via.email,
        for_=user.email,
    )


def user_to_register_from(request: HttpRequest) -> User:
    return models.User(
        name=request.POST["name"],
        email=request.POST["email"],
        password=request.POST["password1"],
    )


def user_to_authorize_from(request: HttpRequest) -> Optional[User]:
    return auth.authenticate(
        request,
        username=request.POST["name"],
        password=request.POST["password"],
    )


class user_redis_repository:
    def _connect() -> Redis:
        return get_redis_connection("registration")

    def save(user: User) -> None:
        connection = user_redis_repository._connect()

        password_hash = hashing.hashed(user.password)

        connection.hset(user.email, "name", user.name)
        connection.hset(user.email, "password_hash", password_hash)

        connection.expire(user.email, confirmation.activity_minutes * 60)

    @do(optionally)
    def get_of(do: Do, email: types_.Email) -> User:
        connection = user_redis_repository._connect()

        name = do(connection.hget)(email, "name").decode()
        password_hash = do(connection.hget)(email, "password_hash").decode()

        password = hashing.unhashed(password_hash)

        return models.User(name=name, email=email, password=password)

    def delete(user: User) -> None:
        connection = user_redis_repository._connect()
        connection.hdel(user.email, "name", "password_hash")


@obj.of
class user_django_orm_repository:
    get_by_email = fun(_.models.User.objects.filter(email=e).first())
    get_by_name = fun(_.models.User.objects.filter(name=n).first())

    save = models.User.save
    has = fun(u.id.is_not(None))


authorized = io(flipped(auth.login))
