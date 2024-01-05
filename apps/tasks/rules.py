from enum import Enum

from act import val


@val
class tasks:
    class Status(Enum):
        active = 1
        done = 2
        failed = 3


@val
class users:
    @val
    class default_task_settings:
        remove_on: tasks.Status = tasks.Status.done
