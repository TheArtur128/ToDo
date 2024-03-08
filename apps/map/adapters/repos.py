from typing import Optional

from act import tmap, optionally, obj

from apps.map import models
from apps.map.core import rules


type User = models.User


def _task_settings_of(
    task_settings_record: models.TaskSettings,
) -> rules.TaskSettings:
    return rules.TaskSettings(
        remove_task_on=rules.TaskStatus(task_settings_record.remove_task_on),
    )


def _submap_of(map_record: models.Map) -> rules.Submap:
    global_task_settings = optionally(_task_settings_of)(
        map_record.global_task_settings,
    )

    return rules.Submap(
        id=map_record.id,
        user_position=rules.Position(x=map_record.x, y=map_record.y),
        global_task_settings=global_task_settings,
        tasks=tmap(_task_of, map_record.tasks),
    )


def _task_of(task_record: models.Task) -> rules.Task:
    return rules.Task(
        id=task_record.id,
        description=task_record.description,
        status=rules.TaskStatus(task_record.status),
        settings=optionally(_task_settings_of)(task_record.settings),
        submap=optionally(_submap_of)(task_record),
        position=rules.Position(x=task_record.x, y=task_record.y),
    )


def _top_map_of(map_top_record: models.MapTop) -> rules.TopMap:
    global_task_settings = optionally(_task_settings_of)(
        map_top_record.global_task_settings,
    )

    user_position = rules.Position(
        x=map_top_record.map.x,
        y=map_top_record.map.y,
    )

    tasks = tmap(_task_of, map_top_record.map.tasks)

    return rules.TopMap(
        id=map_top_record.id,
        name=map_top_record.name,
        global_task_settings=global_task_settings,
        user_position=user_position,
        tasks=tasks,
        next=optionally(_top_map_of)(map_top_record.next),
        previous=optionally(_top_map_of)(map_top_record.previous),
    )


def _user_of(user_record: models.User) -> rules.User:
    global_task_settings = optionally(_task_settings_of)(
        user_record.global_task_settings,
    )

    return rules.User(
        id=user_record.id,
        maps=tmap(_top_map_of, user_record.maps),
        global_task_settings=global_task_settings,
    )


@obj
class django_orm_users:
    def user_of(self, id: int) -> Optional[User]:
        return optionally(_user_of)(models.User.objects.filter(id=id).first())

    def saved(self, user: rules.User) -> User:
        settings_record = self._create_task_settings(user.global_task_settings)

        user_record = models.User.objects.create(
            id=user.id,
            global_task_settings=settings_record,
        )

        for top_map in user.maps:
            self._create_map(top_map, user_record)

        return user_record

    def _create_map(
        self,
        top_map: Optional[rules.TopMap],
        user_record: models.User,
    ) -> models.MapTop:
        if top_map is None:
            return None

        map_record = models.Map.objects.create(
            x=top_map.user_position.x,
            y=top_map.user_position.y,
        )

        return models.MapTop.objects.create(
            id=top_map.id,
            map=map_record,
            user=user_record,
            name=top_map.name,
        )

    @staticmethod
    @optionally
    def _create_task_settings(
        settings_record: rules.TaskSettings,
    ) -> models.TaskSettings:
        return models.TaskSettings.objects.create(
            remove_task_on=settings_record.remove_task_on.value
        )
