from typing import Callable

from act import obj, val, by
from django.http import HttpRequest

from apps.access import adapters, cases, types_, lib


type User = adapters.User


@obj
class registration:
    _cases = cases.registration
    _adapters = adapters.registration

    def open_using(
        self,
        name=types_.Username,
        email=types_.Email,
        password=types_.Password,
    ) -> types_.URL:
        return self._cases.open_using(
            name, email, password,
            is_there_user_named=self._adapters.is_there_user_named,
            confirmation_page_url_of=self._adapters.confirmation_page_url_of,
            remember=self._adapters.remember,
        )

    def complete_by(self, email: types_.Email, request: HttpRequest) -> User:
        return self._cases.complete_by(
            email,
            remembered_user_of=self._adapters.remembered_user_of,
            is_there_user_named=self._adapters.is_there_user_named,
            forget=self._adapters.forget,
            save=self._adapters.save,
            authorize=self._adapters.authorize |by| request,
        )


@obj
class authorization:
    _cases = cases.authorization

    _opening = adapters.authorization.opening
    _completing = adapters.authorization.completing

    def open_using(
        self,
        name: types_.Username,
        password: types_.Password,
        request: HttpRequest,
    ) -> types_.URL:
        return self._cases.open_using(
            name,
            password,
            user_of=self._opening.user_of |by| request,
            confirmation_page_url_of=self._opening.confirmation_page_url_of,
        )

    def complete_by(self, email: types_.Email, request: HttpRequest) -> User:
        return self._cases.complete_by(
            email,
            user_of=self._completing.user_of,
            authorize=self._completing.authorize |by| request,
        )


@val
class access_recovery:
    _open_confirmation_for = adapters.access_recovery.opening.confirmation_for

    @as_method
    @do(optionally)
    def open_via_email_using(
        do,
        self,
        email: types_.Email,
        new_password: types_.Password,
    ) -> Optional[types_.URL]:
        return cases.access_recovery.open_using(
            contextual(new_password, email),
            user_of=do(adapters.access_recovery.opening.get_user_by_email),
            access_to_confirm_for=do(self._open_confirmation_for),
        )

    @as_method
    @do(optionally)
    def open_via_name_using(
        do,
        self,
        name: types_.Username,
        new_password: types_.Password,
    ) -> Optional[types_.URL]:
        return cases.access_recovery.open_using(
            contextual(new_password, name),
            user_of=do(adapters.access_recovery.opening.get_user_by_name),
            access_to_confirm_for=do(self._open_confirmation_for),
        )

    @do(optionally)
    def complete_by(do: Do, email: types_.Email, request: HttpRequest) -> User:
        return cases.access_recovery.complete_by(
            email,
            user_of=do(adapters.access_recovery.completion.user_of),
            with_new_password=do(
                adapters.access_recovery.completion.with_new_password
            ),
            authorized=(
                adapters.access_recovery.completion.authorized |by| request
            ),
        )


@val
class profile:
    def of(user: User) -> lib.ui.LazyPage:
        return cases.profile.of(
            user,
            user_of=adapters.profile.user_of,
            profile_of=adapters.profile.profile_of,
        )
