from typing import TypeAlias

from act import by
from django.http import HttpRequest

from access import adapters, core
from shared.tools import io
from shared.transactions import do, rollbackable, Do
from shared.types_ import URL, Email


User: TypeAlias = adapters.User


@do(rollbackable.optionally)
def open_registration_port_for(do: Do, user: User) -> URL:
    registration = core.registration_for(
        user,
        is_already_registered=adapters.user_django_orm_repository.has,
        access_to_confirm_for=do(adapters.open_confirmation_port_for),
        remembering_for=adapters.user_local_repository.save,
    )

    return registration.access_to_confirm


@do(rollbackable.optionally)
def register_user_by(do: Do, email: Email, *, request: HttpRequest) -> User:
    return core.register_user_by(
        email,
        remembered_user_by=do(adapters.user_local_repository.get_of),
        is_already_registered=adapters.user_django_orm_repository.has,
        authorized=adapters.authorized |by| request,
        saved=io(adapters.user_django_orm_repository.save),
    )


@do(rollbackable.optionally)
def authorize_user_by(do: Do, email: Email, *, request: HttpRequest) -> User:
    return core.authorize_user_by(
        email,
        user_by=do(adapters.user_django_orm_repository.get_of),
        authorized=adapters.authorized |by| request,
    )
