from act import ok, bad


__all__ = ("status_of", )


def status_of(condition: bool) -> ok[None] | bad[None]:
    return ok(None) if condition else bad(None)
