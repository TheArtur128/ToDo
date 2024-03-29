from enum import Enum, auto
from string import ascii_lowercase, ascii_uppercase, digits, punctuation
from typing import Iterable

from act import type, val, by

from apps.access.core import errors


type Username = str
type Email = str
type Password = str
type PasswordHash = str


AuthenticationUser = type(name=Username, email=Email, password=Password)
RegistrationUser = type(name=Username, email=Email, password_hash=PasswordHash)
User = type(id=int, name=Username, email=Email, password_hash=PasswordHash)


@val
class passwords:
    type MediumPasswordError = errors.PasswordWithoutPunctuation
    type WeakPasswordError = (
        errors.PasswordTooShort
        | errors.PasswordWithoutAsciiLowercase
        | errors.PasswordWithoutAsciiUppercase
        | errors.PasswordWithoutDigits
    )

    class Powers(Enum):
        weak: int = auto()
        medium: int = auto()
        strong: int = auto()

    def power_of(password: Password) -> Powers:
        errors = tuple(passwords.is_valid(password))

        if any(map(isinstance |by| passwords.WeakPasswordError, errors)):
            return passwords.Powers.weak
        if any(map(isinstance |by| passwords.MediumPasswordError, errors)):
            return passwords.Powers.medium

        return passwords.Powers.strong

    def is_valid(password: Password) -> Iterable[errors.Access]:
        if len(password) < 8:
            yield errors.PasswordTooShort()

        if len(password) > 128:
            yield errors.PasswordTooLong()

        if set(password) - set(ascii_lowercase) == set(password):
            yield errors.PasswordWithoutAsciiLowercase()

        if set(password) - set(ascii_uppercase) == set(password):
            yield errors.PasswordWithoutAsciiUppercase()

        if set(password) - set(digits) == set(password):
            yield errors.PasswordWithoutDigits()
 
        if set(password) - set(punctuation) == set(password):
            yield errors.PasswordWithoutPunctuation()

    def is_remembered(
        password: Password,
        repeated_password: Password,
    ) -> Iterable[errors.Access]:
        if password != repeated_password:
            yield errors.PasswordMismatch()


@val
class users:
    def is_valid(user: User) -> Iterable[errors.Access]:
        if len(user.name) > 128:
            yield errors.UsernameTooLong()
        elif len(user.name) < 2:
            yield errors.UsernameTooShort()


@val
class registration_users:
    def is_valid(user: RegistrationUser) -> Iterable[errors.Access]:
        yield from users.is_valid(user)


@val
class authentication_users:
    def is_valid(user: AuthenticationUser) -> Iterable[errors.Access]:
        yield from users.is_valid(user)
        yield from passwords.is_valid(user.password)

