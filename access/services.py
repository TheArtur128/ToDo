from typing import TypeAlias

from act import by
from django.http import HttpRequest

from access import adapters, cases
from shared.tools import io
from shared.transactions import do, rollbackable, Do
from shared.types_ import URL, Email


User: TypeAlias = adapters.User


@do(rollbackable.optionally)
def open_registration_port_for(do: Do, user: User) -> URL:
    registration = cases.registration_for(
        user,
        is_already_registered=adapters.user_django_orm_repository.has,
        access_to_confirm_for=do(adapters.open_registration_confirmation_for),
        remembering_for=adapters.user_local_repository.save,
    )

    return registration.access_to_confirm


@do(rollbackable.optionally)
def register_by(do: Do, email: Email, *, request: HttpRequest) -> User:
    return cases.register_by(
        email,
        remembered_user_by=do(adapters.user_local_repository.get_of),
        is_already_registered=adapters.user_django_orm_repository.has,
        authorized=adapters.authorized |by| request,
        saved=io(adapters.user_django_orm_repository.save),
    )


@do(rollbackable.optionally)
def authorization_by(do: Do, request: HttpRequest) -> URL:
    return cases.authorization_by(
        request,
        user_by=do(adapters.user_to_authorize_from),
        open_port_for=do(adapters.open_authorization_confirmation_for),
    )


@do(rollbackable.optionally)
def authorize_by(do: Do, email: Email, *, request: HttpRequest) -> User:
    return cases.authorize_by(
        email,
        user_by=do(adapters.user_django_orm_repository.get_by_email),
        authorized=adapters.authorized |by| request,
    )


@do(rollbackable.optionally)
def access_recovery_via_email_by(do: Do, email: Email) -> URL:
    return cases.access_recovery_by(
        email,
        user_by=do(adapters.user_django_orm_repository.get_by_email),
        open_port_for=do(adapters.open_access_recovery_confirmation_for),
    )


@do(rollbackable.optionally)
def access_recovery_via_name_by(do: Do, name: str) -> URL:
    return cases.access_recovery_by(
        name,
        user_by=do(adapters.user_django_orm_repository.get_by_name),
        open_port_for=do(adapters.open_access_recovery_confirmation_for),
    )
