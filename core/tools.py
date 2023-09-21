from typing import Iterable, Callable, Any, TypeAlias, Optional

from act import (
    temp, obj, Special, bad, will, to, then, eventually, returnly,
    optionally, Pm, V, R
)

from core.types import Annotaton


def name_enum_of(annotated: temp(__annotations__=Iterable[str])) -> obj:
    return obj.of({name: name for name in annotated.__annotations__.keys()})


def bad_or(value: Special[None, V]) -> V | bad[None]:
    return bad(None) if value is None else value
