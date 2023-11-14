from typing import Literal

from act import val, obj, do, Do, optionally, fbind_by, then, not_, by
from django.http import HttpRequest

from apps.access import adapters, cases, types_


type User = adapters.User


@val
class registration:
    @do(optionally)
    def open_using(do: Do, request: HttpRequest) -> types_.URL:
        return cases.registration.open_using(
            request,
            user_of=do(adapters.registration.user_of),
            access_to_confirm_for=do(adapters.registration.confirmation.add),
        )

    @do(optionally, else_=False)
    def complete_by(
        do: Do, email: types_.Email, request: HttpRequest
    ) -> Literal[True]:
        cases.registration.complete_by(
            email,
            user_of=do(adapters.registration.confirmation.pop_by),
            registered=adapters.registration.registered,
            authorized=adapters.registration.authorized |by| request,
        )

        return True


@val
class authorization:
    @do(optionally)
    def open_using(do: Do, request: HttpRequest) -> types_.URL:
        access_to_confirm_for = do(adapters.authorization.open_confirmation_for)

        return cases.authorization.open_using(
            request,
            user_of=do(adapters.authorization.user_to_open_by),
            access_to_confirm_for=access_to_confirm_for,
        )

    @fbind_by(... |then>> not_(None))
    @do(optionally)
    def complete_by(do: Do, email: types_.Email, request: HttpRequest) -> User:
        return cases.authorization.complete_by(
            email,
            user_of=do(adapters.authorization.user_to_complate_by),
            authorized=adapters.authorization.authorized |by| request,
        )


@obj
class access_recovery:
    _open_confirmation_for = adapters.access_recovery.open_confirmation_for

    @do(optionally)
    def open_via_email_using(do, self, email: types_.Email) -> types_.URL:
        return cases.access_recovery.open_using(
            email,
            user_of=do(adapters.access_recovery.get_user_by_email),
            access_to_confirm_for=do(self._open_confirmation_for),
        )

    @do(optionally)
    def open_via_name_using(do, self, name: str) -> types_.URL:
        return cases.access_recovery.open_using(
            name,
            user_of=do(adapters.access_recovery.get_user_by_name),
            access_to_confirm_for=do(self._open_confirmation_for),
        )
