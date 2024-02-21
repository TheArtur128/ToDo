from typing import Optional, Any

from act import (
    val, obj, do, optionally, sculpture_of, fbind_by, then, original_of, io
)
from django.contrib import auth
from django.contrib.auth.hashers import make_password, check_password
from django.http import HttpRequest
from django_redis import get_redis_connection

from apps.access import rules, models
from apps.access.types_ import URL, Email, Password, PasswordHash, Username
from apps.access.lib import confirmation, created_user_of, Sculpture


type _UserSculpture = Sculpture[rules.User, models.User]


def _for_rules(user: models.User) -> _UserSculpture:
    return sculpture_of(user, password_hash="password")


_as_rule_getter = fbind_by(... |then>> optionally(_for_rules))


@val
class _user_django_orm_repository:
    def save(user: rules.User) -> _UserSculpture:
        user = created_user_of(user.name, user.email, user.password_hash)
        return _for_rules(user)

    def has_named(name: Username) -> bool:
        return models.User.objects.filter(name=name).exists()

    def has_with_email(email: Email) -> bool:
        return models.User.objects.filter(email=email).exists()

    @_as_rule_getter
    def get_by_email(email: Email) -> Optional[_UserSculpture]:
        return models.User.objects.filter(email=email).first()

    @_as_rule_getter
    def get_by_name(name: Username) -> Optional[_UserSculpture]:
        return models.User.objects.filter(name=name).first()


@obj
class _user_redis_repository:
    _connection = get_redis_connection("accounts")
    _activity_seconds = confirmation.activity_minutes * 60

    def save(self, user: rules.User) -> None:
        self._connection.hset(user.email, "name", user.name)
        self._connection.hset(user.email, "password_hash", user.password_hash)

        self._connection.expire(user.email, self._activity_seconds)

    @do(optionally)
    def get_by(do, self, email: Email) -> Optional[rules.User]:
        name = do(self._connection.hget)(email, "name").decode()

        password_hash = do(self._connection.hget)(email, "password_hash")
        password_hash = password_hash.decode()

        return rules.User(name, email, password_hash)

    def delete(self, user: rules.User) -> None:
        self._connection.hdel(user.email, "name", "password_hash")


@obj
class _password_hash_redis_repository:
    _connection = get_redis_connection("passwords")

    def save_under(self, email: Email, password_hash: PasswordHash) -> None:
        self._connection.set(email, password_hash)
        self._connection.expire(email, confirmation.activity_minutes * 60)

    @do(optionally)
    def get_by(do, self, email: Email) -> Optional[PasswordHash]:
        return do(self._connection.get)(email).decode()

    def delete(self, email: Email) -> None:
        self._connection.delete(email)


def _authorize(user: Sculpture[Any, models.User], request: HttpRequest) -> None:
    auth.login(request, original_of(user))


@val
class registration:
    def is_there_user_named(name: Username) -> bool:
        return _user_django_orm_repository.has_named(name)

    def is_there_user_with_email(email: Email) -> bool:
        return _user_django_orm_repository.has_with_email(email)

    def confirmation_page_url_of(email: Email) -> Optional[URL]:
        return confirmation.open_port_of(
            confirmation.subjects.registration,
            confirmation.via.email,
            for_=email,
        )

    def hash_of(password: Password) -> PasswordHash:
        return make_password(password)

    def remember(user: rules.User) -> None:
        _user_redis_repository.save(user)

    def remembered_user_of(email: Email) -> Optional[rules.User]:
        return _user_redis_repository.get_by(email)

    @io
    def forgotten(user: rules.User):
        _user_redis_repository.delete(user)

    def saved(user: rules.User):
        _user_django_orm_repository.save(user)

    authorize = _authorize


@val
class authorization:
    @val
    class opening:
        def user_of(name: Username) -> Optional[_UserSculpture]:
            return _user_django_orm_repository.get_by_name(name)

        def is_hash_of(password: Password, password_hash: PasswordHash) -> bool:
            return check_password(password, password_hash)

        def confirmation_page_url_of(user: rules.User) -> Optional[URL]:
            return confirmation.open_port_of(
                confirmation.subjects.authorization,
                confirmation.via.email,
                for_=user.email,
            )

    @val
    class completion:
        user_of = _user_django_orm_repository.get_by_email
        authorize = _authorize


@val
class access_recovery:
    @val
    class opening:
        def get_user_by_email(email: Email) -> models.User:
            return _user_django_orm_repository.get_by_email(email)

        def get_user_by_name(name: Username) -> models.User:
            return _user_django_orm_repository.get_by_name(name)

        def confirmation_page_url_of(user: rules.User) -> Optional[URL]:
            return confirmation.open_port_of(
                confirmation.subjects.access_recovery,
                confirmation.via.email,
                for_=user.email,
            )

        def hash_of(password: Password) -> PasswordHash:
            return make_password(password)

        def remember_under(email: Email, password_hash: PasswordHash) -> None:
            _password_hash_redis_repository.save_under(email, password_hash)

    @val
    class completion:
        def user_of(email: Email) -> rules.User:
            user = _user_django_orm_repository.get_by_email(email)
            return access_recovery.completion._user_sculpture_of(user)

        def remebered_password_hash_of(email: Email) -> Optional[PasswordHash]:
            return _password_hash_redis_repository.get_by(email)

        def forget_password_hash_under(email: Email) -> None:
            _password_hash_redis_repository.delete(email)

        def update(user: _UserSculpture) -> None:
            original_of(user).save()

        authorize = _authorize
