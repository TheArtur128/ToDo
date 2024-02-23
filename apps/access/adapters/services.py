from typing import Optional, Any

from act import val, original_of
from django.contrib import auth
from django.contrib.auth.hashers import make_password, check_password
from django.http import HttpRequest

from apps.access.adapters import models, types_
from apps.access.core import rules
from apps.access.core.types_ import URL, Email
from apps.access.lib import confirmation


class _Authorizable:
    def __init__(self, request: HttpRequest = None) -> None:
        self.__request = request

    def authorized[U: types_.Sculpture[Any, models.User]](self, user: U) -> U:
        auth.login(self.__request, original_of(user))
        return user


@val
class registration:
    Completion = _Authorizable

    @val
    class opening:
        hash_of = make_password

        def confirmation_page_url_of(email: Email) -> Optional[URL]:
            return confirmation.open_port_of(
                confirmation.subjects.registration,
                confirmation.via.email,
                for_=email,
            )


@val
class authorization:
    Completion = _Authorizable
    
    @val
    class opening:
        is_hash_of = check_password

        def confirmation_page_url_of(user: rules.User) -> Optional[URL]:
            return confirmation.open_port_of(
                confirmation.subjects.authorization,
                confirmation.via.email,
                for_=user.email,
            )


@val
class access_recovery:
    Completion = _Authorizable

    @val
    class opening:
        hash_of = make_password

        def confirmation_page_url_of(user: rules.User) -> Optional[URL]:
            return confirmation.open_port_of(
                confirmation.subjects.access_recovery,
                confirmation.via.email,
                for_=user.email,
            )
