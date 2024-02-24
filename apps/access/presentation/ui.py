from string import punctuation
from typing import Any, Iterable

from act import val, type

from apps.access import lib


User = type(name=str, email=str)


@val
class profile:
    def page_of(user: User) -> lib.ui.LazyPage:
        context = dict(name=user.name, email=lib.half_hidden(user.email, 4))

        return lib.ui.LazyPage("access/profile.html", context)


def username_messages_of(error: Any) -> Iterable[str]:
    if error == "UsernameTooShort":
        yield "Your name must be more than 2 characters."

    elif error == "UsernameTooLong":
        yield "Your name must be 128 characters maximum."


def password_messages_of(error: Any) -> Iterable[str]:
    if error == "PasswordTooShort":
        yield "Your password must be at least 8 characters long."

    if error == "PasswordTooLong":
        yield "Your password must be 128 characters maximum."

    if error == "PasswordWithoutAsciiLowercase":
        yield "Your password must contain at least one lowercase Latin letter."

    if error == "PasswordWithoutAsciiUppercase":
        yield "Your password must contain at least one uppercase Latin letter."

    if error == "PasswordWithoutDigits":
        yield "Your password must contain at least one number."

    if error == "PasswordWithoutPunctuation":
        yield (
            "Your password must contain at least "
            f"one character from {punctuation}."
        )


def user_validation_messages_of(error: Any) -> Iterable[str]:
    yield from username_messages_of(error)
    yield from password_messages_of(error)


def password_repetition_messages_of(error: Any) -> Iterable[str]:
    if error == "PasswordMismatch":
        yield "Repeated password is not correct."


def completion_messages_of(error: Any) -> Iterable[str]:
    if error == "NoUser":
        yield "Go back and enter your data again."


default_exitsing_message = "Make sure you entered your account data correctly."


def confirmation_messages_of(error: Any) -> Iterable[str]:
    if error == "Confirmation":
        yield (
            "Unable to confirm. "
            "Try again after a while or contact tech. "
            "support if all attempts are unsuccessful."
        )


@val
class registration:
    @val
    class opening:
        def messages_of(
            error: Any,
            name: str,
            email: str,
        ) -> Iterable[str]:
            if error == "UserExists":
                yield f"\"{name}\" name is already taken."

            if error == "EmailExists":
                yield f"\"{email}\" email is already taken."

            yield from password_repetition_messages_of(error)

            if error == "EmailConfirmation":
                yield "Choose another email or try again after a while."

            yield from user_validation_messages_of(error)

    @val
    class completion:
        def messages_of(
            error: Any,
            login_page_url: str,
        ) -> Iterable[str]:
            if error == "UserExists":
                yield (
                    f"User registration has already been completed. "
                    f"Login <a href=\"{login_page_url}\">here<a/>"
                )

            yield from completion_messages_of(error)


@val
class authorization:
    @val
    class opening:
        def messages_of(error: Any) -> Iterable[str]:
            if error in ("NoUser", "IncorrectPassword"):
                yield default_exitsing_message

            yield from confirmation_messages_of(error)

    @val
    class completion:
        def messages_of(error: Any) -> Iterable[str]:
            yield completion_messages_of(error)


@val
class access_recovery:
    @val
    class opening:
        def using_name_messages_of(error: Any) -> Iterable[str]:
            if error == "NoUser":
                yield "Make sure you entered your name correctly."

            yield from access_recovery.opening._other_messages_of(error)

        def using_email_messages_of(error: Any) -> Iterable[str]:
            if error == "NoUser":
                yield "Make sure you entered your email correctly."

            yield from access_recovery.opening._other_messages_of(error)

        def _other_messages_of(error: Any) -> Iterable[str]:
            yield from password_messages_of(error)
            yield from password_repetition_messages_of(error)
            yield from confirmation_messages_of(error)
