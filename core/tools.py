from typing import Iterable

from act import ok, bad, temp, obj


def status_of(condition: bool) -> ok[None] | bad[None]:
    return ok(None) if condition else bad(None)

