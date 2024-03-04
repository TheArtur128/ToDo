from functools import partial
from typing import Callable, Concatenate, Union, Iterator

from act import of, ok, Pm, PmA, PmD


def _to_decorate_with_parameters[A, R](
    callback_handler: Callable[Concatenate[Callable[[], A], PmD], R]
) -> Callable[PmD, Callable[Callable[PmA, A], Callable[PmA, R]]]:
    def get_decorator(
        *callback_handler_args: PmD.args,
        **callback_handler_kwargs: PmD.kwargs,
    ):
        def decorator(action: Callable[PmA, A]) -> Callable[PmA, R]:
            def wrapper(
                *action_args: PmA.args,
                **action_kwargs: PmA.kwargs,
            ) -> R:
                callback = partial(action, *action_args, **action_kwargs)
                return callback_handler(
                    callback,
                    *callback_handler_args,
                    **callback_handler_kwargs
                )

            return wrapper
        return decorator
    return get_decorator


def _to_decorate_without_parameters[A, R](
    callback_handler: Callable[Callable[[], A], R]
) -> Callable[Callable[Pm, A], Callable[Pm, R]]:
    def decorator(action: Callable[Pm, A]) -> Callable[Pm, R]:
        def wrapper(*args: Pm.args, **kwargs: Pm.kwargs) -> R:
            callback = partial(action, *args, **kwargs)
            return callback_handler(callback)

        return wrapper
    return decorator


def to_decorate[A, R](with_parameters: bool = False) -> Union[
    Callable[
        Callable[Callable[[], A], R],
        Callable[Callable[Pm, A], Callable[Pm, R]]
    ],
    Callable[
        Callable[Concatenate[Callable[[], A], PmD], R],
        Callable[PmD, Callable[Callable[PmA, A], Callable[PmA, R]]]
    ],
]:
    return (
        _to_decorate_with_parameters
        if with_parameters
        else _to_decorate_without_parameters
    )


class ReturningIterator[V](Iterator):
    def __init__(self, iterator: Iterator[V]) -> None:
        self.__iterator = iterator

    def __next__(self) -> V:
        try:
            return next(self.__iterator)
        except StopIteration as stop:
            if stop.value is None:
                raise stop from stop

            return stop.value.value if of(ok, stop.value) else stop.value
