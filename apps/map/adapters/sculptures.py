from typing import Iterator, Callable

from act import tmap, optionally, Unia, type, val
from django.db.models.query import QuerySet

from apps.map import models
from apps.map.core import rules


class QuerySetSculpture[OriginalT, RuleT, OwnerT]:
    owner = property(lambda self: self.__owner)

    def __init__(
        self,
        for_rules: Callable[OriginalT, RuleT],
        query_set: "QuerySet[OriginalT, OriginalT]",
        owner: OwnerT,
    ) -> None:
        self.query_set = query_set
        self.__for_rules = for_rules
        self.__owner = owner

    def __iter__(self) -> Iterator[RuleT]:
        return map(self.__for_rules, self.query_set)


def _to_make_sculpture[V, R](make: Callable[V, R]) -> Callable[
    V,
    Unia[R, type(_sculpture_original=V)]
]:
    def make_sculpture(value):
        result = make(value)

        return val(result) & val(_sculpture_original=value)

    return make_sculpture


@_to_make_sculpture
def task_settings_of(
    task_settings_record: models.TaskSettings,
) -> rules.TaskSettings:
    return rules.TaskSettings(
        remove_task_on=rules.TaskStatus(task_settings_record.remove_task_on),
    )


@_to_make_sculpture
def submap_of(map_record: models.Map) -> rules.Submap:
    global_task_settings = optionally(task_settings_of)(
        map_record.global_task_settings,
    )

    return rules.Submap(
        id=map_record.id,
        user_position=rules.Position(x=map_record.x, y=map_record.y),
        global_task_settings=global_task_settings,
        tasks=QuerySetSculpture(task_of, map_record.tasks.all(), map_record),
    )


@_to_make_sculpture
def task_of(task_record: models.Task) -> rules.Task:
    return rules.Task(
        id=task_record.id,
        description=task_record.description,
        status=rules.TaskStatus(task_record.status),
        settings=optionally(task_settings_of)(task_record.settings),
        submap=optionally(submap_of)(task_record),
        position=rules.Position(x=task_record.x, y=task_record.y),
    )


@_to_make_sculpture
def top_map_of(map_top_record: models.MapTop) -> rules.TopMap:
    global_task_settings = optionally(task_settings_of)(
        map_top_record.global_task_settings,
    )

    user_position = rules.Position(
        x=map_top_record.map.x,
        y=map_top_record.map.y,
    )

    tasks = QuerySetSculpture(
        task_of,
        map_top_record.map.tasks.all(),
        map_top_record,
    )

    return rules.TopMap(
        id=map_top_record.id,
        name=map_top_record.name,
        global_task_settings=global_task_settings,
        user_position=user_position,
        tasks=tasks,
        next=optionally(top_map_of)(map_top_record.next),
        previous=optionally(top_map_of)(map_top_record.previous),
    )


@_to_make_sculpture
def user_of(user_record: models.User) -> rules.User:
    global_task_settings = optionally(task_settings_of)(
        user_record.global_task_settings,
    )

    return rules.User(
        id=user_record.id,
        maps=tmap(top_map_of, user_record.maps.all()),
        global_task_settings=global_task_settings,
    )
