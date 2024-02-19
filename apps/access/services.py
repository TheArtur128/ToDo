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


@obj
class access_recovery:
    _cases = cases.access_recovery

    _opening = adapters.access_recovery.opening

    def _open_using[ID: types_.Email | types_.Username](
        self,
        id: ID,
        new_password: types_.Password,
        user_of: Callable[ID, User],
    ) -> types_.URL:
        return self._cases.open_using(
            id,
            new_password,
            user_of=user_of,
            confirmation_page_url_of=self._opening.confirmation_page_url_of,
            hash_of=self._opening.hash_of,
            remember_under=self._opening.remember_under,
        )

    open_via_email_using = (
        staticmethod(_open_using |by| _opening.get_user_by_email)
    )
    open_via_name_using = (
        staticmethod(_open_using |by| _opening.get_user_by_name)
    )

    def complete_by(self, email: types_.Email, request: HttpRequest) -> User:
        remebered_password_hash_of = self._completing.remebered_password_hash_of
        forget_password_hash_under = self._completing.forget_password_hash_under

        return self._cases.complete_by(
            email,
            user_of=self._completing.user_of,
            remebered_password_hash_of=remebered_password_hash_of,
            forget_password_hash_under=forget_password_hash_under,
            authorize=self._completing.authorize |by| request,
        )


@val
class profile:
    def of(user: User) -> lib.ui.LazyPage:
        return cases.profile.of(
            user,
            user_of=adapters.profile.user_of,
            profile_of=adapters.profile.profile_of,
        )
