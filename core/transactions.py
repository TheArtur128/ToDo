@via_indexer
def RollbackableBy(
    parameters_annotation: Annotaton,
    return_annotation: Annotation,
) -> temp:
    return temp(rollback=Callable[parameters_annotation, return_annotation])


class TransactionError(Exception):
    ...


class TransactionRollback(Exception):
    ...


class Transaction(Generic[O]):
    __NO_RESULT: ClassVar[Flag] = flag_about("__NO_RESULT")
    __result: R | __NO_RESULT = __NO_RESULT

    def __init__(
        self,
        *operations: Special[RollbackableBy[[], R] | Callable[[], Any], O],
    ) -> None:
        self.__operations = tuple(operations)

    def __enter__(self) -> Callable[[], bool]:
        def get_result() -> contextual[bool, R]:
            if self.__result is not type(self).__NO_RESULT:
                return self.__result

            raise TransactionError("getting results of an active transaction")

        return get_result

    def __exit__(
        self,
        error_type: Optional[Type[Special[TransactionRollback, Exception]]],
        error: Special[TransactionRollback, Exception],
        traceback: Any,
    ) -> bool:
        if not issubclass(error_type, TransactionRollback):
            return False

        self.__result = self.__rollback_operations()

        return True

    def run(self) -> bool:
        with self as get_ok:
            for operation in filter(callable, self.__operations):
                operation()

        return get_ok()

    def __rollback_operations(self) -> bool:
        ok = True

        for operation in reversed(self.__operations):
            if isinstance(operation, RollbackableBy[[], Any]):
                ok = False
                operation.rollback()

        return ok


def rollback() -> NoReturn:
    raise TransactionRollback("rollback a transaction outside of a transaction")


@func
class _rollbackable:
    __arguments_to_rollback: Optional[Arguments] = None

    def __init__(
        self,
        operation: ActionOf[Pm, R] & RollbackableBy[Pm, L] | ActionOf[Pm, R],
    ) -> None:
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
    def maybe(result: Special[bad[R]]) -> bool:
        return of(bad, result)

    @_rollbackable_on
    def either(result: Special[left[Any]]) -> bool:
        return of(left, result)
