from act import obj, flipped, io, fun
from act.cursors.static import u, r, e, n, _
from django.contrib import auth

from access.input import confirmation
from shared import models
from shared.types_ import Email


type User = models.User


open_registration_confirmation_for = fun(_.confirmation.open_port_of(
    confirmation.subjects.registration,
    confirmation.via.email,
    for_=u.email,
))


open_access_recovery_confirmation_for = fun(_.confirmation.open_port_of(
    confirmation.subjects.access_recovery,
    confirmation.via.email,
    for_=u.email,
))


open_authorization_confirmation_for = fun(_.confirmation.open_port_of(
    confirmation.subjects.authorization,
    confirmation.via.email,
    for_=u.email,
))


user_to_register_from = fun(_.User(
    name=r.POST["name"],
    email=r.POST["email"],
    password=r.POST["password1"],

))


user_to_authorize_from = fun(_.auth.authenticate(
    r,
    username=r.POST["name"],
    password=r.POST["password"],
))


@obj.of
class user_local_repository:
    _config: dict[Email, User] = dict()

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
