from enum import Enum
from typing import Iterable

from act import type


class TaskStatus(Enum):
    active = 1
    done = 2
    failed = 3


TaskSettings = type(remove_task_on=TaskStatus)
default_new_task_settings = TaskSettings(remove_task_on=TaskStatus.done)

Task = type(status=TaskStatus, settings=TaskSettings)
User = type(tasks=Iterable[Task], new_task_settings=TaskSettings)
