from secrets import token_urlsafe
from typing import Callable

from act import to

from apps.shared.types_ import Token


def token_generator_with(*, length: int) -> Callable[[], Token]:
    byte_number = int(length * 3 / 4)

    return token_urlsafe |to| byte_number
