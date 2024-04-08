from functools import wraps
from typing import Iterator, Callable, Iterable, Self

from act import optionally, obj, type, val, partially, Unia, out, by, Pm, Cn
from django import db

from apps.map import core, models, ui


class QuerySetSculpture[OriginalT, RuleT, OwnerT]:
    owner = property(lambda self: self.__owner)

    def __init__(
        self,
        for_rules: Callable[OriginalT, RuleT],
        query_set: "db.models.query.QuerySet[OriginalT, OriginalT]",
        owner: OwnerT,
    ) -> None:
        self.query_set = query_set
        self.__for_rules = for_rules
        self.__owner = owner

    def __iter__(self) -> Iterator[RuleT]:
        return map(self.__for_rules, self.query_set)


type _DjangoOrmRecord = db.models.Model


@partially
def _with_original_which_is[O, V](
    original: O,
    value: V,
) -> Unia[V, type(_sculpture_original=O)]:
    return val(value, _sculpture_original=original)


@obj
class rules:
    def task_settings_of(
        self,
        task_settings_record: models.TaskSettings,
    ) -> core.rules.TaskSettings:
        remove_task_on = core.rules.TaskStatus(
            task_settings_record.remove_task_on,
        )

        return _with_original_which_is(task_settings_record)(
            core.rules.TaskSettings(remove_task_on=remove_task_on)
        )

    def submap_of(self, map_record: models.Map) -> core.rules.Submap:
        global_task_settings = optionally(self.task_settings_of)(
            map_record.global_task_settings,
        )

        tasks = QuerySetSculpture(
            self.task_of,
            map_record.tasks.all(),
            map_record,
        )

        return _with_original_which_is(map_record)(core.rules.Submap(
            id=map_record.id,
            user_position=core.rules.Position(x=map_record.x, y=map_record.y),
            global_task_settings=global_task_settings,
            tasks=tasks,
        ))

    def task_of(self, task_record: models.Task) -> core.rules.Task:
        return _with_original_which_is(task_record)(core.rules.Task(
            id=task_record.id,
            description=task_record.description,
            status=core.rules.TaskStatus(task_record.status),
            settings=optionally(self.task_settings_of)(task_record.settings),
            submap=optionally(self.submap_of)(task_record.submap),
            position=core.rules.Position(x=task_record.x, y=task_record.y),
        ))

    def top_map_of(self, map_top_record: models.MapTop) -> core.rules.TopMap:
        map_ = map_top_record.map

        global_task_settings = optionally(self.task_settings_of)(
            map_.global_task_settings,
        )

        user_position = core.rules.Position(x=map_.x, y=map_.y)

        tasks = QuerySetSculpture(
            self.task_of,
            map_.tasks.all(),
            map_top_record,
        )

        return _with_original_which_is(map_top_record)(core.rules.TopMap(
            id=map_top_record.id,
            name=map_top_record.name,
            global_task_settings=global_task_settings,
            user_position=user_position,
            tasks=tasks,
            next=optionally(self.top_map_of)(map_top_record.next),
            previous=optionally(self.top_map_of)(out(map_top_record).previous),
        ))

    def user_of(self, user_record: models.User) -> core.rules.User:
        global_task_settings = optionally(self.task_settings_of)(
            user_record.global_task_settings,
        )

        maps = QuerySetSculpture(
            self.top_map_of,
            user_record.maps.all(),
            user_record,
        )

        return _with_original_which_is(user_record)(core.rules.User(
            id=user_record.id,
            maps=maps,
            global_task_settings=global_task_settings,
        ))


class DjangoOrmRecords:
    def __init__(self, *, are_saved: bool = False) -> None:
        self._are_saved = are_saved

    @staticmethod
    def __lazy_record_converter_method_decorator[
        S: Self,
        V,
        R: _DjangoOrmRecord,
    ](
        record_of: Callable[Cn[S, V, Pm], R]
    ) -> Callable[Cn[S, V, Pm], R]:
        @wraps(record_of)
        def decorated_converter(
            self: S,
            value: V,
            *args: Pm.args,
            **kwargs: Pm.kwargs,
        ) -> R:
            if not self._are_saved:
                original = out(value)._sculpture_original

                if isinstance(original, _DjangoOrmRecord):
                    return original

            return record_of(self, value, *args, **kwargs)

        return decorated_converter

    @__lazy_record_converter_method_decorator
    def task_settings_of(
        self,
        task_settings: core.rules.TaskSettings,
    ) -> models.TaskSettings:
        return self._current(models.TaskSettings(
            remove_task_on=task_settings.remove_task_on.value,
        ))

    @__lazy_record_converter_method_decorator
    def user_of(self, user: core.rules.User) -> models.User:
        settings_record = self.task_settings_of(user.global_task_settings)

        user_record = self._current(models.User(
            id=user.id,
            global_task_settings=settings_record,
        ))

        self.__map_tops_of(user.maps, user_record)

        return user_record

    @__lazy_record_converter_method_decorator
    def map_top_of(
        self,
        top_map: core.rules.TopMap,
        user_record: models.User,
    ) -> models.MapTop:
        map_record = self.map_of(top_map)

        map_top_of = optionally(self.map_top_of |by| user_record)

        return self._current(models.MapTop(
            id=top_map.id,
            map=map_record,
            user=user_record,
            name=top_map.name,
            next=map_top_of(map_record.next),
            previous=map_top_of(out(map_record).previous),
        ))

    @__lazy_record_converter_method_decorator
    def map_of(self, top_map: core.rules.TopMap) -> models.Map:
        task_settings_of = optionally(self.task_settings_of)
        settings_record = task_settings_of(top_map.global_task_settings)

        map_record = self._current(models.Map(
            global_task_settings=settings_record,
            x=top_map.user_position.x,
            y=top_map.user_position.y,
        ))

        self.__tasks_of(top_map.tasks, map_record)

        return map_record

    @__lazy_record_converter_method_decorator
    def task_of(
        self,
        task: core.rules.Task,
        root_map_record: models.Map,
    ) -> models.Task:
        return self._current(models.Task(
            id=task.id,
            root_map=root_map_record,
            description=task.description,
            status=task.status.value,
            settings=optionally(self.task_settings_of)(task.settings),
            x=task.position.x,
            y=task.position.y,
            submap=optionally(self.submap_of)(task.submap)
        ))

    @__lazy_record_converter_method_decorator
    def submap_of(self, submap: core.rules.Submap) -> models.Map:
        submap_record = self._current(models.Map(
            id=submap.id,
            global_task_settings=optionally(self.task_settings_of)(
                submap.global_task_settings
            ),
            x=submap.user_position.x,
            y=submap.user_position.y,
        ))

        self.__tasks_of(submap.tasks, submap_record)

        return submap_record

    def _current[R: _DjangoOrmRecord](self, record: R) -> R:
        if self._are_saved:
            record.save()

        return record

    def __records_of[V, R: _DjangoOrmRecord](
        self,
        values: Iterable[V],
        *,
        record_of: Callable[V, R],
    ) -> tuple[R, ...]:
        if self._are_saved and not isinstance(values, QuerySetSculpture):
            return tuple(record_of(value) for value in values)

        return tuple()

    def __map_tops_of(
        self,
        maps: Iterable[core.rules.TopMap],
        user_record: models.User
    ) -> tuple[models.MapTop, ...]:
        record_of = self.map_top_of |by| user_record

        return self.__records_of(maps, record_of=record_of)

    def __tasks_of(
        self,
        tasks: Iterable[core.rules.Task],
        map_record: models.Map,
    ) -> tuple[models.Task, ...]:
        return self.__records_of(tasks, record_of=self.task_of |by| map_record)


@val
class renderable:
    def task_of(task_record: models.Task) -> ui.Task:
        return ui.Task(
            description=task_record.description,
            x=task_record.x,
            y=task_record.y,
            is_done=task_record.status != models.Task.Status.active,
        )
