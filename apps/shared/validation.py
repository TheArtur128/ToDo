from typing import Optional, Callable, Iterable, Literal

from act import contextualizing, flag_about, of, raise_

from apps.shared.errors import all_errors_of
from apps.shared.lib import to_decorate, ReturningIterator


def same[V](value: Optional[V], *, else_: Exception) -> V:
    if value is None:
        raise else_ from else_

    return value


def exists[V, M](value: Optional[V], message: M) -> tuple[M]:
    return (message, ) if value is None else tuple()


def valid[V](value: V, validate: Callable[V, Iterable[Exception]]) -> V:
    checks = tuple(validate(value))

    if len(checks) != 0:
        raise ExceptionGroup(str(), checks)

    return value


as_result = contextualizing(flag_about("as_result"))

last = contextualizing(flag_about("last"))


def latest[V](values: Iterable[V]) -> Iterable[V | last[V]]:
    value_iter = iter(values)

    try:
        previous = next(value_iter)
    except StopIteration:
        return

    while True:
        try:
            current = next(value_iter)
        except StopIteration:
            yield last(previous)
            return

        yield previous
        previous = current


type MultipleErrorCalculus[R, E: Exception] = (
    Iterable[R | as_result[R] | E | last[E] | Literal[raise_]]
)


@to_decorate()
def to_raise_multiple_errors[R, E: Exception](
    callback: Callable[[], MultipleErrorCalculus[R, E]],
) -> R:
    errors = list()
    calculus = ReturningIterator(iter(callback()))

    for result in calculus:
        if isinstance(result, Exception):
            errors.extend(all_errors_of(result))
            continue

        if of(last, result):
            errors.extend(all_errors_of(result.value))
            break

        if result is raise_:
            if len(errors) == 0:
                continue

            break


        if of(as_result, result):
            result = result.value

        if len(errors) == 0:
            return result

        break

    if len(errors) == 0:
        return None

    raise ExceptionGroup(str(), errors)
