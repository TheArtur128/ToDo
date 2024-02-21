from typing import Callable, Iterable

from act import flat, Special


class Application(Exception): ...


def messages_of[ErrorT: Exception, R](
    group: ExceptionGroup,
    *searchers: Callable[ErrorT, Iterable[R]],
) -> tuple[R]:
    message_groups = tuple(
        tuple(search_using(error) for search_using in searchers)
        for error in group.exceptions
    )

    if any(len(message_group) == 0 for message_group in message_groups):
        raise group from group

    return flat(flat(message_groups))


def all_errors_of(error_root: Special[ExceptionGroup, Exception]) -> Iterable[
    Exception
]:
    if isinstance(error_root, ExceptionGroup):
        yield from error_root.exceptions
    else:
        yield error_root
