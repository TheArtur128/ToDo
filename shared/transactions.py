from typing import (
    Generic, ClassVar, Callable, Any, Optional, Type, Literal, NoReturn
)

from act import (
    temp, obj, Flag, flag_about, Arguments, via_indexer, bad, left, of, func,
    contextual, partially, Special, R, O, L, Pm
)

from shared.types import Annotation, ActionOf


@via_indexer
def RollbackableBy(
    parameters_annotation: Annotation,
    return_annotation: Annotation,
) -> temp:
    return temp(rollback=Callable[parameters_annotation, return_annotation])


class _TransactionCursor(Generic[R]):
    operations = property(c.__operations)

    def __init__(
        self,
        operations: Iterable[Special[
            RollbackableBy[[], R] | Callable[[], Any],
            O,
        ]],
        result: R,
    ) -> None:
        self.__operations = tuple(operations)
        self.result = result

    def rollback(self) -> None:
        for operation in reversed(self.__operations):
            if isinstance(operation, RollbackableBy[[], Any]):
                operation.rollback()

    def combined_with(self, other: Self) -> Self:
        return _TransactionCursor(
            (*self.operations, *other.operations),
            result=self.result,
        )


class _TransactionRollback(Generic[M, R], Exception):
    def __init__(
        self,
        message: str = str(),
        cursor: Optional[_TransactionCursor] = None
    ) -> None:
        super().__init__(message)
        self.cursor = cursor


class Transaction(Generic[O]):
    def __init__(
        self,
        *operations: Special[RollbackableBy[[], R] | Callable[[], Any], O],
    ) -> None:
        self.__cursor = _TransactionCursor(operations, True)

    def __enter__(self) -> Callable[[], bool]:
        return to(self.__cursor.result)

    def __exit__(
        self,
        error_type: Optional[Type[Special[_TransactionRollback, Exception]]],
        rollback: Special[_TransactionRollback, Exception],
        traceback: Any,
    ) -> bool:
        if not issubclass(error_type, _TransactionRollback):
            return False

        self.__cursor.result = False
        self.__cursor_when(rollback).rollback()

        return True

    def run(self) -> bool:
        with self as get_ok:
            for operation in filter(callable, self.__cursor.operations):
                operation()

        return get_ok()

    def __cursor_when(
        self,
        rollback: _TransactionRollback[R],
    ) -> _TransactionRollback[R]:
        if rollback.cursor is None:
            return self.__cursor

        return self.__cursor.combined_with(rollback.cursor)


def rollback(*, cursor: Optional[_TransactionCursor] = None) -> NoReturn:
    raise _TransactionRollback(
        "rollback a transaction outside of a transaction",
        cursor,
    )


@func
class _rollbackable:
    __OPERATION_ANNOTATION: ClassVar[Final[TypeAlias[Annotation]]]
    __OPERATION_ANNOTATION = (
        ActionOf[Pm, R] & RollbackableBy[Pm, L] | ActionOf[Pm, R]
    )

    __arguments_to_rollback: Optional[Arguments] = None

    def __new__(cls, operation: __OPERATION_ANNOTATION | Self) -> Self:
        if isinstance(operation, _rollbackable):
            return operation

        return super().__new__(cls)

    def __init__(self, operation: __OPERATION_ANNOTATION) -> None:
        self.__operation = operation

    def __call__(self, *args: Pm.args, **kwargs: Pm.kwargs) -> R:
        self.__arguments_to_rollback = Arguments(args, kwargs)

        return self.__operation(*args, **kwargs)

    def rollback(self) -> Optional[L]:
        can_rollback = (
            self.__arguments_to_rollback is not None
            and isinstance(self.__operation, RollbackableBy[..., Any])
        )

        if not can_rollback:
            return None

        return self.__arguments_to_rollback.call(self.__operation.rollback)


@partially
def _rollbackable_on(
    is_to_rollback: Callable[R, bool],
    operation: ActionOf[Pm, R] & RollbackableBy[Pm, L] | ActionOf[Pm, R],
) -> ActionOf[Pm, R] & RollbackableBy[[], Optional[L]]:
    operation = _rollbackable(operation)

    @obj.of
    class rollbackable_operation:
        def __call__(*args: Pm.args, **kwargs: Pm.kwargs) -> R:
            result = operation(*args, **kwargs)

            if is_to_rollback(result):
                rollback()

            return result

        def rollback(*args: Pm.args, **kwargs: Pm.kwargs) -> L:
            return operation.rollback(*args, **kwargs)

    return rollbackable_operation


@obj.of
class rollbackable:
    __call__ = _rollbackable

    @_rollbackable_on
    def binary(result: Special[Literal[False]]) -> bool:
        return result is False

    @_rollbackable_on
    def optionally(result: Special[None]) -> bool:
        return result is None

    @_rollbackable_on
    def maybe(result: Special[bad[Any]]) -> bool:
        return of(bad, result)

    @_rollbackable_on
    def either(result: Special[left[Any]]) -> bool:
        return of(left, result)


def transaction(action: Callable[Pm, R]) -> Callable[Pm, R]:
    @wraps(action)
    def decorated(*args: Pm.args, **kwargs: Pm.kwargs) -> Special[R]:
        try:
            result = action(*args, **kwargs)
        except _TransactionRollback as rollback:
            rollback.cursor.rollback()

            return rollback.cursor.result

    return decorated


# Not implemetned
def for_transaction() -> ...:
    ...
