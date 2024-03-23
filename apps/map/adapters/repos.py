from typing import Optional, Any

from act import optionally, val, obj, original_of, type
from django.db import transaction
from rest_framework.request import Request

from apps.map import models
from apps.map.adapters import sculptures
from apps.map.core import rules


type User = models.User
type Task = models.Task


@obj
class django_orm_users:
    def user_of(self, id: int) -> Optional[User]:
        user_record = models.User.objects.filter(id=id).first()

        return optionally(sculptures.user_of)(user_record)

    def saved(self, user: rules.User) -> User:
        settings_record = self._create_task_settings(user.global_task_settings)

        user_record = models.User.objects.create(
            id=user.id,
            global_task_settings=settings_record,
        )

        for top_map in user.maps:
            self._create_map(top_map, user_record)

        return sculptures.user_of(user_record)

    def _create_map(
        self,
        top_map: rules.TopMap,
        user_record: models.User,
    ) -> models.MapTop:
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


class django_orm_case_tasks:
    class Users:
        def __init__(self, request: Request) -> None:
            self.__request = request

        def get_current(self) -> Optional[rules.User]:
            return optionally(sculptures.user_of)(
                models.User.objects.filter(id=self.__request.user.id).first()
            )

    @val
    class top_maps:
        def top_map_of(id: int) -> Optional[rules.TopMap]:
            top = models.MapTop.objects.filter(id=id).first()

            return optionally(sculptures.top_map_of)(top)

    @val
    class tasks:
        def saved[S: type(_sculpture_original=models.Task)](
            task_sculpture: S,
        ) -> S:
            task_record = original_of(task_sculpture)
            task_record.save()

            return task_sculpture


def django_orm_uow(*_: Any, **__: Any) -> transaction.Atomic:
    return transaction.atomic()
