from secrets import token_urlsafe
from typing import Callable, Optional, Iterable

from act import fun, then, to, Unia, flat
from act.cursors.static import t

from apps.shared.types_ import Token


type Sculpture[FormT, OriginalT] = (
    Unia[FormT, type(_sculpture_original=OriginalT)]
)


def token_generator_with(*, length: int) -> Callable[[], Token]:
    if (length - 1) % 4 == 0:
        generate = token_generator_with(length=length + 1)
        cut = fun(t[:length])

        return fun(generate |then>> cut)

    byte_number = int(length * 3 / 4)

    return token_urlsafe |to| byte_number


def half_hidden(
    line: str,
    number_of_not_hidden: int,
    *,
    hidden_symbol: str = '#',
) -> str:
    if len(line) < number_of_not_hidden * 2:
        return hidden_symbol * len(line)

    start = line[:number_of_not_hidden]
    middle = hidden_symbol * (len(line) - number_of_not_hidden * 2)
    end = line[-number_of_not_hidden:]

    return start + middle + end


def same[V](value: Optional[V], *, else_: Exception) -> V:
    if value is None:
        raise else_ from else_

    return value


def valid[V](value: V, validate: Callable[V, Iterable[Exception]]) -> V:
    checks = tuple(validate(value))

    if len(checks) != 0:
        raise ExceptionGroup(str(), checks)

    return value


def messages_of[GroupT: ExceptionGroup, ErrorT: Exception, R](
    group: GroupT,
    *searchers: Callable[ErrorT, Iterable[R]],
) -> tuple[R]:
    messages = flat(
        search_using(error)
        for search_using in searchers
        for error in group.exceptions
    )

    if len(messages) == 0:
        raise group from group

    return messages
