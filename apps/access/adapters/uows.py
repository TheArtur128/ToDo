from typing import Any

from django.db import transaction


def django_orm(*_: Any, **__: Any) -> transaction.Atomic:
    return transaction.atomic()
