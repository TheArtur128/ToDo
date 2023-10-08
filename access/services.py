from act import obj, do, Do, optionally, fbind_by, then, on, by, io
from django.http import HttpRequest

from access import adapters, cases
from shared.types_ import URL, Email


type User = adapters.User


@obj.of
class registration:
    @do(optionally)
    def open_using(do: Do, request: HttpRequest) -> URL:
        access_to_confirm_for = do(adapters.open_registration_confirmation_for)

        opening = cases.registration.open_using(
            request,
            user_of=adapters.user_to_register_from,
            is_already_registered=adapters.user_django_orm_repository.has,
            access_to_confirm_for=access_to_confirm_for,
            memorization_of=adapters.user_local_repository.save,
        )

        return opening.access_to_confirm

    @fbind_by(... |then>> on(None, False, else_=True))
    @do(optionally)
    def complete_by(do: Do, email: Email, *, request: HttpRequest) -> User:
        return cases.registration.complete_by(
            email,
            memorized_user_of=do(adapters.user_local_repository.get_of),
            is_already_registered=adapters.user_django_orm_repository.has,
            authorized=adapters.authorized |by| request,
            saving_for=io(adapters.user_django_orm_repository.save),
        )


@obj.of
class authorization:
    @do(optionally)
    def open_using(do: Do, request: HttpRequest) -> URL:
        access_to_confirm_for = do(adapters.open_authorization_confirmation_for)

        return cases.authorization.open_using(
            request,
            user_of=do(adapters.user_to_authorize_from),
            access_to_confirm_for=access_to_confirm_for,
        )

    @fbind_by(... |then>> on(None, False, else_=True))
    @do(optionally)
    def complete_by(do: Do, email: Email, *, request: HttpRequest) -> User:
        return cases.authorization.complete_by(
            email,
            user_of=do(adapters.user_django_orm_repository.get_by_email),
            authorized=adapters.authorized |by| request,
        )


@obj.of
class access_recovery:
    @do(optionally)
    def open_via_email_using(do: Do, email: Email) -> URL:
        access_to_confirm_for = do(
            adapters.open_access_recovery_confirmation_for
        )

        return cases.access_recovery.open_using(
            email,
            user_of=do(adapters.user_django_orm_repository.get_by_email),
            access_to_confirm_for=access_to_confirm_for,
        )

    @do(optionally)
    def open_via_name_using(do: Do, name: str) -> URL:
        access_to_confirm_for = do(
            adapters.open_access_recovery_confirmation_for
        )

        return cases.access_recovery_by(
            name,
            user_of=do(adapters.user_django_orm_repository.get_by_name),
            access_to_confirm_for=access_to_confirm_for,
        )
