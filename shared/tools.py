from dataclasses import dataclass
from typing import Iterable, TypeVar, Self, Callable, Concatenate

from act import temp, obj, bad, to, Special, Unia, Pm, V, A, R


def name_enum_of(annotated: temp(__annotations__=Iterable[str])) -> obj:
    return obj.of({name: name for name in annotated.__annotations__.keys()})


def bad_or(value: Special[None, V]) -> V | bad[None]:
    return bad(None) if value is None else value


def struct(type_: type) -> Unia[temp, temp(T=TypeVar)]:
    template = temp.of(dataclass(type_))
    with_type_var = obj(T=TypeVar(f"{type_.__name__}T", bound=template))

    return template & with_type_var


class _CallingInfix:
    def __init__(self, name: str, *, argument_to_bind: A = None) -> None:
        self.__name = name
        self.__argument_to_bind = argument_to_bind

    def __str__(self) -> str:
        return f"|{self.__name}|"

    def __ror__(self, argument_to_bind: A) -> Self:
        return _CallingInfix(self.__name, argument_to_bind=argument_to_bind)

    def __or__(
        self,
        action: Callable[Concatenate[A, Pm], R],
    ) -> Callable[Pm, R]:
        return action(self.__argument_to_bind)


frm = _CallingInfix('frm')
