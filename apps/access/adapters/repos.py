from typing import Optional

from act import (
    val, obj, do, optionally, sculpture_of, fbind_by, then, original_of
)
from django_redis import get_redis_connection

from apps.access import models
from apps.access.core import rules
from apps.access.lib import confirmation, Sculpture


type User = Sculpture[rules.User, models.User]


def _for_rules(user: models.User) -> User:
    return sculpture_of(user, password_hash="password")


_as_rule_getter = fbind_by(... |then>> optionally(_for_rules))


@val
class user_django_orm_repository:
    def saved(user: rules.RegistrationUser) -> User:
        return _for_rules(models.User.objects.create(
            name=user.name,
            email=user.email,
            password=user.password_hash,
        ))

    def committed[U: User](user: U) -> U:
        record = original_of(user)
        record.save()

        return user

    def has_named(name: str) -> bool:
        return models.User.objects.filter(name=name).exists()

    def has_with_email(email: str) -> bool:
        return models.User.objects.filter(email=email).exists()

    @_as_rule_getter
    def id_user_of(id: int) -> Optional[User]:
        return models.User.objects.filter(id=id).first()

    @_as_rule_getter
    def get_by_email(email: str) -> Optional[User]:
        return models.User.objects.filter(email=email).first()

    @_as_rule_getter
    def get_by_name(name: str) -> Optional[User]:
        return models.User.objects.filter(name=name).first()


@obj
class user_redis_repository:
    _connection = get_redis_connection("accounts")
    _activity_seconds = confirmation.activity_minutes * 60

    def saved(self, user: rules.RegistrationUser) -> rules.RegistrationUser:
        self._connection.hset(user.email, "name", user.name)
        self._connection.hset(user.email, "password_hash", user.password_hash)

        self._connection.expire(user.email, self._activity_seconds)

        return user

    @do(optionally)
    def get_by(do, self, email: str) -> Optional[rules.RegistrationUser]:
        name = do(self._connection.hget)(email, "name").decode()

        password_hash = do(self._connection.hget)(email, "password_hash")
        password_hash = password_hash.decode()

        return rules.RegistrationUser(
            name=name,
            email=email,
            password_hash=password_hash,
        )

    def deleted(self, user: rules.RegistrationUser) -> rules.RegistrationUser:
        self._connection.hdel(user.email, "name", "password_hash")
        return user


@obj
class redis_password_hash_repository:
    type _PasswordHash = str
    _connection = get_redis_connection("passwords")

    def saved_under(
        self,
        email: str,
        password_hash: _PasswordHash,
    ) -> _PasswordHash:
        self._connection.set(email, password_hash)
        self._connection.expire(email, confirmation.activity_minutes * 60)

        return password_hash

    @do(optionally)
    def get_by(do, self, email: str) -> Optional[_PasswordHash]:
        return do(self._connection.get)(email).decode()

    def deleted(self, email: str) -> None:
        self._connection.delete(email)
        return email


@val
class access_recovery:
    name_user_repository = val(user_of=user_django_orm_repository.get_by_name)
    email_user_repository = val(user_of=user_django_orm_repository.get_by_email)
