from typing import Literal

from act import val, do, Do, optionally, fbind_by, then, not_, io, by
from django.http import HttpRequest

from apps.access import adapters, cases, types_


type User = adapters.User


@val
class registration:
    @do(optionally)
    def open_using(do: Do, request: HttpRequest) -> types_.URL:
        return cases.registration.open_using(
            request,
            user_of=do(adapters.user_to_register_from),
            access_to_confirm_for=do(adapters.registration_confirmation.add),
        )

    @do(optionally, else_=False)
    def complete_by(
        do: Do, email: types_.Email, *, request: HttpRequest
    ) -> Literal[True]:
        cases.registration.complete_by(
            email,
            user_of=do(adapters.registration_confirmation.pop_by),
            registered=do(adapters.registered),
            authorized=adapters.authorized |by| request,
        )

        return True


@val
class authorization:
    @do(optionally)
    def open_using(do: Do, request: HttpRequest) -> types_.URL:
        access_to_confirm_for = do(adapters.open_authorization_confirmation_for)

        return cases.authorization.open_using(
            request,
            user_of=do(adapters.user_to_authorize_from),
            access_to_confirm_for=access_to_confirm_for,
        )

    @fbind_by(... |then>> not_(None))
    @do(optionally)
    def complete_by(
        do: Do, email: types_.Email, *, request: HttpRequest
    ) -> User:
        return cases.authorization.complete_by(
            email,
            user_of=do(adapters.user_django_orm_repository.get_by_email),
            authorized=io(adapters.authorize) |by| request,
        )


@val
class access_recovery:
    @do(optionally)
    def open_via_email_using(do: Do, email: types_.Email) -> types_.URL:
        access_to_confirm_for = do(
            adapters.open_access_recovery_confirmation_for
        )

        return cases.access_recovery.open_using(
            email,
            user_of=do(adapters.user_django_orm_repository.get_by_email),
            access_to_confirm_for=access_to_confirm_for,
        )

    @do(optionally)
    def open_via_name_using(do: Do, name: str) -> types_.URL:
        access_to_confirm_for = do(
            adapters.open_access_recovery_confirmation_for
        )

        return cases.access_recovery_by(
            name,
            user_of=do(adapters.user_django_orm_repository.get_by_name),
            access_to_confirm_for=access_to_confirm_for,
        )
