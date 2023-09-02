from typing import Iterable

from act import temp, obj


__all__ = ("name_enum_of", )


def name_enum_of(annotated: temp(__annotations__=Iterable[str])) -> obj:
    return obj.of({name: name for name in annotated.__annotations__.keys()})
