from dataclasses import dataclass
from typing import Iterable, TypeVar

from act import temp, obj, Special, bad, Unia, V


def name_enum_of(annotated: temp(__annotations__=Iterable[str])) -> obj:
    return obj.of({name: name for name in annotated.__annotations__.keys()})


def bad_or(value: Special[None, V]) -> V | bad[None]:
    return bad(None) if value is None else value


def struct(type_: type) -> Unia[temp, temp(T=TypeVar)]:
    template = temp.of(dataclass(type_))
    with_type_var = obj(T=TypeVar(f"{type_.__name__}T", bound=template))

    return template & with_type_var
