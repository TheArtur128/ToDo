from typing import Callable

from act import obj, by
from django.http import HttpRequest

from apps.access import adapters, cases, types_


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
            hash_of=self._adapters.hash_of,
            remember=self._adapters.remember,
        )

    def complete_by(self, email: types_.Email, request: HttpRequest) -> User:
        return self._cases.complete_by(
            email,
            remembered_user_of=self._adapters.remembered_user_of,
            forgotten=self._adapters.forgotten,
            is_there_user_named=self._adapters.is_there_user_named,
            saved=self._adapters.saved,
            authorized=self._adapters.authorized |by| request,
        )


@obj
class authorization:
    _cases = cases.authorization

    _opening = adapters.authorization.opening
    _completion = adapters.authorization.completion

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
            is_hash_of=self._opening.is_hash_of,
            confirmation_page_url_of=self._opening.confirmation_page_url_of,
        )

    def complete_by(self, email: types_.Email, request: HttpRequest) -> User:
        return self._cases.complete_by(
            email,
            user_of=self._completion.user_of,
            authorized=self._completion.authorized |by| request,
        )


@obj
class access_recovery:
    _cases = cases.access_recovery

    _opening = adapters.access_recovery.opening
    _completion = adapters.access_recovery.completion

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

    open_via_email_using = _open_using |by| _opening.get_user_by_email
    open_via_name_using = _open_using |by| _opening.get_user_by_name

    def complete_by(self, email: types_.Email, request: HttpRequest) -> User:
        remebered_password_hash_of = self._completion.remebered_password_hash_of
        forget_password_hash_under = self._completion.forget_password_hash_under

        return self._cases.complete_by(
            email,
            user_of=self._completion.user_of,
            remebered_password_hash_of=remebered_password_hash_of,
            forget_password_hash_under=forget_password_hash_under,
            authorize=self._completion.authorize |by| request,
        )
