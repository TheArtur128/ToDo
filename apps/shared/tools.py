from secrets import token_urlsafe
from typing import Callable

from act import fun, then, to
from act.cursors.static import t

from apps.shared.types_ import Token


def token_generator_with(*, length: int) -> Callable[[], Token]:
    if (length - 1) % 4 == 0:
        generate = token_generator_with(length=length + 1)
        cut = fun(t[:length])

        return fun(generate |then>> cut)

    byte_number = int(length * 3 / 4)

    return token_urlsafe |to| byte_number
