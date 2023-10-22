from typing import Optional

from act import obj, flipped, io, fun
from act.cursors.static import u, e, n, _
from django.contrib import auth
from django.http import HttpRequest

from apps.access.input import confirmation, models, types_


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


class UserRedisRepository:
    def __init__(self, key_type: Name) -> None:
        self.__key_type = key_type

    def connect(self) -> Redis:
        return get_redis_connection("registration")

    def save(self, user: User) -> None:



@obj.of
class user_local_repository:
    _config: dict[types_.Email, User] = dict()

    get_of = _config.get
    save = fun(_._config[u.email].ioset(u))
    has = fun(_._config.values_().has(u))


@obj.of
class user_django_orm_repository:
    get_by_email = fun(_.models.User.objects.filter(email=e).first())
    get_by_name = fun(_.models.User.objects.filter(name=n).first())

    save = models.User.save
    has = fun(u.id.is_not(None))


authorized = io(flipped(auth.login))
