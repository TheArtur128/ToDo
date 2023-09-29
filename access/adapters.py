from typing import TypeAlias

from act import obj, flipped, u, r, e, n, _
from django.contrib import auth

from access.input import confirmation
from shared import models
from shared.tools import io
from shared.types_ import Email


User: TypeAlias = models.User


open_registration_confirmation_for = _.confirmation.open_port_of(
    confirmation.subjects.registration,
    confirmation.via.email,
    for_=u.email,
)


user_to_authorize_from = _.auth.authenticate(
    r,
    username=r.POST["name"],
    password=r.POST["password"],
)


@obj.of
class user_local_repository:
    _config: dict[Email, User] = dict()

    get_of = _config.get
    save = _._config[u.email].mset(u)
    has = _._config.values_().has(u)


@obj.of
class user_django_orm_repository:
    get_by_email = _.User.objects.filter(email=e).first._()
    save = User.save
    has = u.id.is_not(None)


authorized = io(flipped(auth.login))
