from typing import Callable, Iterable

from act import flat, Special


def messages_of[R](
    group: ExceptionGroup,
    *searchers: Callable[str, Iterable[R]],
) -> tuple[R]:
    message_groups = tuple(
        tuple(search_using(type(error).__name__) for search_using in searchers)
        for error in group.exceptions
    )

    if any(len(message_group) == 0 for message_group in message_groups):
        raise group from group

    messages = flat(flat(message_groups))

    if len(messages) == 0 and len(group.exceptions) != 0:
        raise group from group

    return messages


def all_errors_of(error_root: Special[ExceptionGroup, Exception]) -> Iterable[
    Exception
]:
    if isinstance(error_root, ExceptionGroup):
        yield from error_root.exceptions
    else:
        yield error_root
