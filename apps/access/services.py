from typing import Optional

from act import val, do, Do, optionally, by, contextual, as_method
from django.http import HttpRequest

from apps.access import adapters, cases, types_, lib


type User = adapters.User


@val
class registration:
    def open_using(
        name=types_.Username,
        email=types_.Email,
        password=types_.Password,
    ) -> types_.URL:
        confirmation_page_url_of = (
            adapters.registration.confirmation_page_url_of
        )

        return cases.registration.open_using(
            name, email, password,
            is_there_user_named=adapters.registration.is_there_user_named,
            confirmation_page_url_of=confirmation_page_url_of,
            remember=adapters.registration.remember,
        )

    def complete_by(email: types_.Email, request: HttpRequest) -> User:
        return cases.registration.complete_by(
            email,
            remembered_user_of=adapters.registration.remembered_user_of,
            is_there_user_named=adapters.registration.is_there_user_named,
            forget=adapters.registration.forget,
            save=adapters.registration.save,
            authorize=adapters.registration.authorize |by| request,
        )


@val
class authorization:
    def open_using(
        name: types_.Username,
        password: types_.Password,
        request: HttpRequest,
    ) -> types_.URL:
        confirmation_page_url_of = (
            adapters.authorization.opening.confirmation_page_url_of
        )

        return cases.authorization.open_using(
            name,
            password,
            user_of=adapters.authorization.opening.user_of |by| request,
            confirmation_page_url_of=confirmation_page_url_of,
        )

    def complete_by(email: types_.Email, request: HttpRequest) -> User:
        return cases.authorization.complete_by(
            email,
            user_of=adapters.authorization.completing.user_of,
            authorize=adapters.authorization.completing.authorize |by| request,
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
