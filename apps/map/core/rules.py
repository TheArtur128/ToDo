from enum import Enum
from typing import Iterable, Optional

from act import type, val


class TaskStatus(Enum):
    active = 1
    done = 2
    failed = 3


TaskSettings = type(remove_task_on=TaskStatus)
Task = type(description=str, status=TaskStatus, settings=Optional[TaskSettings])
User = type(id=int, tasks=Iterable[Task], global_task_settings=TaskSettings)


@val
class users:
    def created_with(id: int) -> User:
        return User(
            id=id,
            tasks=tuple(),
            global_task_settings=TaskSettings(remove_task_on=TaskStatus.done)
        )


@val
class tasks:
    def created_with(description=str) -> Task:
        return Task(
            description=description,
            status=TaskStatus.active,
            settings=None,
        )
