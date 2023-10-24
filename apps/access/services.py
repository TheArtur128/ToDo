from typing import Literal

from act import obj, do, Do, optionally, fbind_by, then, not_, io, by
from django.http import HttpRequest

from apps.access import adapters, cases
from apps.access.input import types_


type User = adapters.User


@obj.of
class registration:
    @do(optionally)
    def open_using(do: Do, request: HttpRequest) -> types_.URL:
        access_to_confirm_for = do(adapters.open_registration_confirmation_for)

        confirmation_page_url = cases.registration.open_using(
            request,
            user_of=adapters.user_to_register_from,
            is_already_registered=adapters.user_django_orm_repository.has,
            access_to_confirm_for=access_to_confirm_for,
            memorize=adapters.user_redis_repository.save,
        )

        return confirmation_page_url.value

    @fbind_by(... |then>> not_(None))
    @do(optionally)
    def complete_by(
        do: Do, email: types_.Email, *, request: HttpRequest
    ) -> Literal[True]:
        cases.registration.complete_by(
            email,
            memorized_user_of=do(adapters.user_redis_repository.get_of),
            forget=adapters.user_redis_repository.delete,
            is_already_registered=adapters.user_django_orm_repository.has,
            saved=io(adapters.user_django_orm_repository.save),
            authorize=adapters.authorize |by| request,
        )

        return True


@obj.of
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
            authorized=adapters.authorized |by| request,
        )


@obj.of
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
