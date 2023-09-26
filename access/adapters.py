from typing import TypeAlias

from act import _, u

import confirmation
from shared import models
from shared.types_ import Email


User: TypeAlias = models.User


open_confirmation_port_for = _.confirmation.contract.open_port_of(
    confirmation.contract.subjects.registration,
    confirmation.contract.via.email,
    for_=u.email,
)


@obj.of
class user_local_repository:
    _config: dict[Email, User] = dict()

    get_of = _config.get
    save = _._config[u.email].mset(u)
    has = _._config.values_().has(u)


@obj.of
class user_django_orm_repository:
    get_of = _.User.objects.filter(email=e).first._()
    save = User.save
    has = u.id.is_not(None)


authorized = returnly(flipped(auth.login))
