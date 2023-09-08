from typing import Iterable

from act import temp, obj, Special, bad, V


__all__ = ("name_enum_of", "bad_or")


def name_enum_of(annotated: temp(__annotations__=Iterable[str])) -> obj:
    return obj.of({name: name for name in annotated.__annotations__.keys()})


def bad_or(value: Special[None, V]) -> V | bad[None]:
    return bad(None) if value is None else value
