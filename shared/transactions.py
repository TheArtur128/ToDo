from dataclasses import dataclass, field
from functools import cached_property, reduce, wraps
from itertools import count
from typing import (
    Generic, ClassVar, Callable, Any, Optional, Type, NoReturn, Iterable,
    Iterator, Self, Generator, TypeAlias, Concatenate, ParamSpec
)

from act import (
    temp, obj, Arguments, ActionChain, via_indexer, bad, left, of, to, by,
    then, tfilter, tmap, partially, flag_about, will, rwill, partial, func, a,
    m, s, c, r, Special, A, B, R, O, L, ActionT, Pm
)

from shared.tools import frm
from shared.types_ import Annotation, ActionOf


@via_indexer
def RollbackableBy(
    parameters_annotation: Annotation,
    return_annotation: Annotation,
) -> temp:
    return temp(rollback=Callable[parameters_annotation, return_annotation])


class _TransactionOperations:
    __Operation: ClassVar[Annotation]
    __Operation = Special[RollbackableBy[[], B] | Callable[[], R]]

    @dataclass(frozen=True)
    class __MarkedOperation:
        operation: "_TransactionOperations.__Operation"
        id: int = field(default_factory=next |to| count())

    bad_result = property(o.__bad_result)
    def __to_map(
        marked_operations_by: Callable[
            Concatenate[Self, Pm],
            tuple[__MarkedOperation],
        ],
    ) -> Callable[Concatenate[Self, Pm], Self]:
        def method(self, *args: Pm.args, **kwargs: Pm.kwargs) -> Self:
            return _TransactionOperations(
                marked_operations_by(self, *args, **kwargs),
                _is_operations_safe=True,
            )

        return method

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

    def __len__(self) -> int:
        return len(self._marked_operations)

    def __contains__(self, operation: Any) -> bool:
        return operation in tmap(m.operation, self._marked_operations)

    def run(self) -> Generator[R, None, None]:
        return (
            marked_operation.operation()
            for marked_operation in self._marked_operations
            if callable(marked_operation.operation)
        )

    def rollback(self) -> tuple[B]:
        return tuple(
            marked_operation.operation.rollback()
            for marked_operation in reversed(self._marked_operations)
            if isinstance(marked_operation.operation, RollbackableBy[[], Any])
        )

    @__to_map
    def mapped_by(
        self,
        decorated: Callable[__Operation, __Operation],
    ) -> tuple[__MarkedOperation]:
        return (tmap |by| self._marked_operations)(
            m.operation |then>> decorated |then>> type(self).__MarkedOperation
        )

    @__to_map
    def filtered_by(
        self,
        is_ok: Callable[__Operation, bool],
    ) -> tuple[__MarkedOperation]:
        return (tfilter |by| self._marked_operations)(m.operation |then>> is_ok)

    @__to_map
    def combined_with(self, other: Self) -> tuple[__MarkedOperation]:
        if self._to_left_than(other):
            return (*self._marked_operations, *other._marked_operations)
        elif other._to_left_than(self):
            return (*other._marked_operations, *self._marked_operations)
        else:
            return tuple(self.__marked_operation_combination_between(
                self._marked_operations,
                other._marked_operations,
            ))

    def _to_left_than(self, other: Self) -> bool:
        if not self._marked_operations or not other._marked_operations:
            return True

        is_strat_on_left = (
            self._marked_operations[0].id <= other._marked_operations[0].id
        )
        is_end_on_left = (
            self._marked_operations[-1].id <= other._marked_operations[-1].id
        )

        return is_strat_on_left and is_end_on_left

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


@dataclass
class _TransactionResult(Generic[R]):
    results: tuple[R] = tuple()
    ok: bool = True


class Transaction(Generic[O]):
    def __init__(
        self,
        *operations: Special[RollbackableBy[[], R] | Callable[[], Any], O],
    ) -> None:
        self.__operations = _TransactionOperations(operations)
        self.__result = _TransactionResult()

    def __enter__(self) -> _TransactionResult[R]:
        return self.__result

    def __exit__(
        self,
        error_type: Optional[Type[Special[_TransactionRollback, Exception]]],
        rollback: Special[_TransactionRollback, Exception],
        traceback: Any,
    ) -> bool:
        if not isinstance(rollback, _TransactionRollback):
            return False

        self.__result.results = self.__operations_when(rollback).rollback()
        self.__result.ok = False

        return True

    def run(self) -> _TransactionResult[R]:
        with self as result:
            for operation in filter(callable, self.__operations.operations):
                operation()

        return result

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


class _rollbackable:
    __OPERATION_ANNOTATION: ClassVar[TypeAlias]
    __OPERATION_ANNOTATION = (
        ActionOf[Pm, R] & RollbackableBy[Pm, L] | ActionOf[Pm, R]
    )

    def __new__(cls, operation: __OPERATION_ANNOTATION | Self) -> Self:
        if isinstance(operation, _rollbackable):
            return operation

        return super().__new__(cls)

    def __init__(self, operation: __OPERATION_ANNOTATION) -> None:
        self.__operation = operation
        self.__arguments_to_rollback = list()

    def __call__(self, *args: Pm.args, **kwargs: Pm.kwargs) -> R:
        result = self.__operation(*args, **kwargs)

        self.__arguments_to_rollback.append(Arguments(args, kwargs))

        return result

    def rollback(self) -> tuple[L]:
        if not isinstance(self.__operation, RollbackableBy[..., Any]):
            return tuple()

        return tmap(
            a.call._(self.__operation.rollback),
            self.__arguments_to_rollback,
        )


_Pm2 = ParamSpec("_Pm2")
_Pm3 = ParamSpec("_Pm3")
_Pm4 = ParamSpec("_Pm4")


@partially
def _map_rollbackable(
    operation: ActionOf[_Pm3, A] & RollbackableBy[_Pm4, B] | ActionOf[_Pm3, A],
    main_decorated: Callable[Callable[_Pm3, A], Callable[Pm, R]],
    rollback_decorated: Callable[Callable[_Pm4, B], Callable[_Pm2, L]] = r,
) -> ActionOf[Pm, R] & RollbackableBy[_Pm2, L] | ActionOf[Pm, R]:
    with_decorated_main = obj(__call__=main_decorated(operation))

    if isinstance(operation, RollbackableBy[..., Any]):
        with_decorated_rollback = obj(
            rollback=rollback_decorated(operation.rollback),
        )
    else:
        with_decorated_rollback = obj()

    return obj.of(operation) & with_decorated_main & with_decorated_rollback


_Mode: TypeAlias = Callable[
    ActionOf[Pm, R] & RollbackableBy[_Pm2, L] | ActionOf[Pm, R],
    ActionOf[Pm, R] & RollbackableBy[[], tuple],
]


def transaction_mode_of(is_to_rollback: Callable[R, bool]) -> _Mode:
    @rwill(partial(_map_rollbackable, rollback_decorated=r))
    def decorated(main: Callable[Pm, R]) -> Callable[Pm, R]:
        @wraps(main)
        def decorated_main(*args: Pm.args, **kwargs: Pm.kwargs) -> R:
            result = main(*args, **kwargs)

            if is_to_rollback(result):
                rollback()

            return result

        return decorated_main

    return func(decorated |then>> _rollbackable)


@obj.of
class rollbackable:
    __call__ = _rollbackable
    map = _map_rollbackable

    binary = transaction_mode_of(r.is_(False))
    optionally = transaction_mode_of(r.is_(None))
    maybe = transaction_mode_of(of(bad))
    either = transaction_mode_of(of(left))


class _TransactionCursor:
    ModeT: ClassVar[TypeAlias] = Callable[Callable[Pm, R], ActionT]
    __network_operations_cache: Optional[_TransactionOperations] = None

    def __init__(self, *modes: ModeT, _parent: Optional[Self] = None) -> None:
        self.__modes = ActionChain(modes)
        self.__operations = _TransactionOperations()
        self.__parent = _parent
        self.__childs = list()

    @property
    def network_operations(self) -> _TransactionOperations:
        if self.__parent is not None:
            return self.__parent.network_operations
        elif self.__network_operations_cache is not None:
            return self.__network_operations_cache
        else:
            self.__network_operations_cache = self._operations.combined_with(
                self._child_operations,
            )

            return self.__network_operations_cache

    @property(s.__operations).setter
    def _operations(self, operations: _TransactionOperations) -> None:
        self.__operations = operations
        self._clear_network_cache()

    @cached_property
    def _child_operations(self) -> _TransactionOperations:
        if not self.__childs:
            return _TransactionOperations()

        return (
            self.__childs
            |frm| (map |to| c._child_operations)
            |frm| (reduce |to| _TransactionOperations.combined_with)
        )

    def __iter__(self) -> Iterator[Self]:
        return map(self.child_for, self.__modes)

    def __call__(self, operation: Callable[Pm, R]) -> ActionT:
        if not self.__is_accepted(operation):
            self.__accept(operation)

        return self.__modes(operation)

    def child_for(self, *modes: ModeT) -> Self:
        child = type(self)(
            *modes,
            else_=self._operations.bad_result,
            _parent=self,
        )

        self._adopt(child)
        return child

    def _adopt(self, child: Self) -> None:
        self.__childs.append(child)
        self._clear_network_cache()

    def _clear_network_cache(self) -> None:
        self.__dict__.pop("_child_operations", None)
        self.__network_operations_cache = None

        if self.__parent is not None:
            self.__parent._clear_network_cache()

    def __accept(self, operation: Callable[Pm, R]) -> None:
        operations_to_combine = _TransactionOperations([operation])
        self._operations = self._operations.combined_with(
            operations_to_combine,
        )

    def __is_accepted(self, operation: Callable[Pm, R]) -> bool:
        return operation in self.network_operations


Do: TypeAlias = _TransactionCursor


@obj.of
class do:
    rollbacks = flag_about("rollbacks")

    def __call__(
        *modes: _TransactionCursor.ModeT,
        else_: Special[rollbacks, L] = None,
    ) -> Callable[Pm, Special[R | L]]:
        @will
        def decorated(
            action: Callable[Concatenate[Do, Pm], R],
            *args: Pm.args,
            **kwargs: Pm.kwargs
        ) -> Callable[Pm, Special[R | L]]:
            cursor = _TransactionCursor(*modes)

            try:
                return action(cursor, *args, **kwargs)
            except _TransactionRollbackMark:
                rollbacks = cursor.network_operations.rollback()

                return rollbacks if else_ == do.rollbacks else else_

        return decorated
