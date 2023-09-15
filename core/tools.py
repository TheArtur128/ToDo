from typing import Iterable

from act import temp, obj, Special, bad, V


__all__ = ("name_enum_of", "bad_or")


def name_enum_of(annotated: temp(__annotations__=Iterable[str])) -> obj:
    return obj.of({name: name for name in annotated.__annotations__.keys()})


def bad_or(value: Special[None, V]) -> V | bad[None]:
    return bad(None) if value is None else value


def _Rollbackable(action_annotation: Annotaton) -> Annotaton:
    return temp(__call__=action_annotation, rollback=Callable[[], Any])


_EventAction: TypeAlias = Callable[[], bool]
_TransactionEvent: TypeAlias = _Rollbackable | _EventAction


def rollbackable_event_by(*args: Pm.args, **kwargs: Pm.kwargs) -> Callable[
    _Rollbackable[Callable[Pm, R]] | Callable[Pm, R],
    _Rollbackable[Callable[[], R]],
]:
    def rollbackable_event_of(
        action: _Rollbackable[Callable[Pm, R]] | Callable[Pm, R]
    ) -> _Rollbackable[Callable[[], R]]:
        event = will(action)(*args, **kwargs)
        rollback = action.rollback if hasattr(action, "rollback") else to(None)

        return obj(__call__=event, rollback=rollback)

    return rollbackable_event_of


def transactionally_for(
    result: R,
    *,
    _completed_events: Iterable[_TransactionEvent] = tuple()
) -> Callable[[..., _TransactionEvent], Optional[R]]:
    def transaction_from(*events: _TransactionEvent) -> Optional[R]:
        if len(events) == 0:
            return result

        ok = events[0]()

        if ok:
            done = (*_completed_events, events[0])

            return transactionally_for(result, _completed_events=done)(
                *events[1:],
            )

        for event in reversed(_completed_events):
            if hasattr(event, "rollback"):
                event.rollback()

    return transaction_from


for_effect = eventually |then>> returnly |then>> optionally
