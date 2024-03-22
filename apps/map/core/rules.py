from enum import Enum
from typing import Iterable, Optional, Self

from act import type, val

from apps.map.core import errors
from apps.map.lib import to_raise_multiple_errors, latest


class TaskStatus(Enum):
    active = 1
    done = 2
    failed = 3


TaskSettings = type(remove_task_on=TaskStatus)
Position = type(x=int, y=int)

TopMap = type(
    id=Optional[int],
    name=str,
    tasks=Iterable["Task"],
    global_task_settings=Optional[TaskSettings],
    user_position=Position,
    next=Optional[Self],
    previous=Optional[Self],
)

Submap = type(
    id=Optional[int],
    tasks=Iterable["Task"],
    global_task_settings=Optional[TaskSettings],
    user_position=Position,
)

Task = type(
    id=Optional[int],
    description=str,
    status=TaskStatus,
    settings=Optional[TaskSettings],
    submap=Optional[Submap],
    position=Position,
)

User = type(
    id=Optional[int],
    maps=Iterable[TopMap],
    global_task_settings=TaskSettings,
)


@val
class maps:
    def is_name_valid(name: str) -> Iterable[errors.Map]:
        if len(name) > 128:
            yield errors.MapNameIsTooLong()

        if len(name) == 0:
            yield errors.MapNameIsTooShort()

    def is_valid(top_map: TopMap) -> Iterable[errors.Map]:
        yield from maps.is_name_valid(top_map.name)


@val
class users:
    @to_raise_multiple_errors
    def created_with(id: int, first_user_map_name: str) -> User:
        yield from latest(maps.is_name_valid(first_user_map_name))

        first_user_map = TopMap(
            id=None,
            name=first_user_map_name,
            tasks=tuple(),
            global_task_settings=None,
            user_position=Position(x=0, y=0),
            next=None,
            previous=None,
        )

        return User(
            id=id,
            maps=[first_user_map],
            global_task_settings=TaskSettings(remove_task_on=TaskStatus.done),
        )


@val
class tasks:
    @to_raise_multiple_errors
    def created_with(description: str, x: int, y: int) -> Task:
        yield from latest(tasks.is_description_valid(description))

        return Task(
            id=None,
            description=description,
            status=TaskStatus.active,
            settings=None,
            submap=None,
            position=Position(x=x, y=y),
        )

    def is_valid(task: Task) -> Iterable[errors.Map]:
        yield from tasks.is_description_valid(task.description)

    def is_description_valid(description: str) -> Iterable[errors.Map]:
        if len(description) > 128:
            yield errors.TaskDescriptionIsTooLong()

        if len(description) == 0:
            yield errors.TaskDescriptionIsTooShort()
