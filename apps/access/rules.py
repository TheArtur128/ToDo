from enum import Enum, auto
from string import ascii_lowercase, ascii_uppercase, digits, punctuation
from typing import Iterable

from act import type, val

from apps.access import errors
from apps.access.types_ import Username, Email, Password, PasswordHash


User = type(name=Username, email=Email, password_hash=PasswordHash)
AuthenticationUser = type(name=Username, email=Email, password=Password)


@val
class passwords:
    class Powers(Enum):
        weak: int = auto()
        medium: int = auto()
        strong: int = auto()

    def power_of(password: Password) -> Powers:
        if len(password) < 8:
            return passwords.Powers.weak
        elif set(password) - set(ascii_lowercase) == set(password):
            return passwords.Powers.weak
        elif set(password) - set(ascii_uppercase) == set(password):
            return passwords.Powers.weak
        elif set(password) - set(digits) == set(password):
            return passwords.Powers.weak
        elif set(password) - set(punctuation) == set(password):
            return passwords.Powers.medium

        return passwords.Powers.strong

    def validate(password: Password) -> Iterable[errors.Access]:
        power = passwords.power_of(password)

        if power is passwords.Powers.weak:
            yield errors.WeakPassword()
        elif power is passwords.Powers.medium:
            yield errors.MediumPassword()

        if len(password) < 128:
            yield errors.PasswordTooLong()


@val
class users:
    def validate(user: User) -> Iterable[errors.Access]:
        if len(user.name) > 128:
            yield errors.UsernameTooLong()
        elif len(user.name) < 2:
            yield errors.UsernameTooShort()


@val
class authentication_users:
    def validate(user: AuthenticationUser) -> Iterable[errors.Access]:
        yield from users.validate(user)
        yield from passwords.validate(user.password)
