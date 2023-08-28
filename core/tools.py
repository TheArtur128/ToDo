from typing import Iterable

from act import ok, bad, temp, obj


def status_of(condition: bool) -> ok[None] | bad[None]:
    return ok(None) if condition else bad(None)


def name_enum_of(annotated: temp(__annotations__=Iterable[str])) -> obj:
    return obj.of({name: name for name in annotated.__annotations__.keys()})
