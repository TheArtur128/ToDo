from functools import reduce
from secrets import token_urlsafe
from typing import Callable, Optional

from act import fun, then, to, merged
from act.cursors.static import t

from apps.shared.types_ import Token


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
        raise else_

    return value


def search[R](error: Exception, *funcs: Callable[Exception, Optional[R]]) -> R:
    assert len(funcs) > 0

    if len(funcs) == 1:
        result = funcs[0](error)
    else:
        raw_results = merged(*funcs)(error)
        result = reduce(lambda a, b: b if a is None else a, raw_results)

    return same(result, else_=error)
