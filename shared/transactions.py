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


class _TransactionOperations(Generic[R]):
    __Operation: ClassVar[Annotation] = Special[RollbackableBy[[], R]]

    @dataclass(frozen=True)
    class __MarkedOperation:
        operation: "_TransactionOperations.__Operation"
        id: int = field(default_factory=next |to| count())

    bad_result = property(o.__bad_result)

    def __init__(
        self,
        operations: Iterable[__Operation | __MarkedOperation] = tuple(),
        bad_result: R = None,
        _is_operations_safe: bool = False,
    ) -> None:
        self.__bad_result = bad_result
        self._marked_operations = (
            operations
            if _is_operations_safe
            else tmap(_TransactionOperations.__MarkedOperation, operations)
        )

    def rollback(self) -> tuple[R]:
        return tuple(
            operation.rollback()
            for operation in reversed(self._marked_operations)
            if isinstance(operation, RollbackableBy[[], Any])
        )

    def combined_with(self, other: Self) -> Self:
        marked_operations = self.__marked_operation_combination_between(
            self._marked_operations,
            other._marked_operations,
        )

        return _TransactionOperations(
            tuple(marked_operations),
            bad_result=self.__bad_result,
            _is_operations_safe=True,
        )

    @staticmethod
    def __marked_operation_combination_between(
        first_ones: tuple[__MarkedOperation],
        second_ones: tuple[__MarkedOperation],
    ) -> Generator[__MarkedOperation, None, None]:
        first_ones_index = 0
        second_ones_index = 0

        is_first_ones_ended = False
        is_second_ones_ended = False

        while True:
            is_first_ones_ended = (
                is_first_ones_ended
                or first_ones_index > len(first_ones) - 1
            )
            is_second_ones_ended = (
                is_second_ones_ended
                or second_ones_index > len(second_ones) - 1
            )

            if is_first_ones_ended and is_second_ones_ended:
                return

            elif is_first_ones_ended:
                yield from second_ones[second_ones_index:]
                is_second_ones_ended = True

            elif is_second_ones_ended:
                yield from first_ones[first_ones_index:]
                is_first_ones_ended = True

            elif (
                first_ones[first_ones_index].id
                <= second_ones[second_ones_index].id
            ):
                yield first_ones[first_ones_index]
                first_ones_index += 1
            else:
                yield second_ones[second_ones_index]
                second_ones_index += 1


class _TransactionRollback(Exception):
    def __init__(
        self,
        message: str = str(),
        operations: _TransactionOperations = _TransactionOperations(),
    ) -> None:
        super().__init__(message)
        self.operations = operations


class Transaction(Generic[O]):
    def __init__(
        self,
        *operations: Special[RollbackableBy[[], R] | Callable[[], Any], O],
    ) -> None:
        self.__operations = _TransactionOperations(operations)

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

    def __operations_when(
        self,
        rollback: _TransactionRollback,
    ) -> _TransactionOperations:
        if rollback.operations is None:
            return self.__operations

        return self.__operations.combined_with(rollback.operations)


def rollback(
    *,
    _operations: Optional[_TransactionOperations] = None,
) -> NoReturn:
    raise _TransactionRollback(
        "rollback a transaction outside of a transaction",
        _operations,
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
        except _TransactionRollback as rollback_mark:
            rollback_mark.operations.rollback()

            return rollback_mark.operations.bad_result

    return decorated


# Not implemetned
def for_transaction() -> ...:
    ...
