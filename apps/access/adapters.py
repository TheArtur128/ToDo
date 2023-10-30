from typing import Optional

from act import obj, flipped, fun, do, Do, optionally, io
from act.cursors.static import u, e, n, _
from django.contrib import auth
from django.http import HttpRequest
from django_redis import get_redis_connection
from redis import Redis

from apps.access.input import confirmation, models, types_, hashing


type User = models.User


@obj.of
class registration_confirmation:
    @do(optionally)
    def add(do: Do, user: User) -> types_.URL:
        confirmation_page_url = do(confirmation.open_port_of)(
            confirmation.subjects.registration,
            confirmation.via.email,
            for_=user.email,
        )

        user_redis_repository.save(user)

        return confirmation_page_url

    @do(optionally)
    def pop_by(do: Do, email: types_.Email) -> User:
        user = do(user_redis_repository.get_by_email)(email)
        user_redis_repository.delete(user)

        return user


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
        username=request.POST["username"],
        password=request.POST["password"],
    )


class user_redis_repository:
    def _connect() -> Redis:
        return get_redis_connection("registration")

    def save(user: User) -> None:
        password_hash = hashing.hashed(user.password)

        connection = user_redis_repository._connect()

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

    has = fun(u.id.is_not(None))

    def save(user: User) -> None:
        user.set_password(user.password)
        user.save()


authorized = io(flipped(auth.login))
