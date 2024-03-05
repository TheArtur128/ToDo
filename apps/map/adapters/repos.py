from typing import Optional

from act import obj, optionally

from apps.map import models
from apps.map.core import rules


type User = models.User


@obj
class django_orm_users:
    def user_of(self, id: int) -> Optional[User]:
        return models.User.objects.filter(id=id).first()

    def saved(self, user: rules.User) -> User:
        global_task_settings_record = self._create_task_settings(
            user.global_task_settings
        )

        user_record = models.User.objects.create(
            id=user.id,
            global_task_settings=global_task_settings_record,
        )

        for task in user.tasks:
            self._create_task(task, user_record)

        return user_record

    def _create_task(
        self,
        task: rules.Task,
        user_record: models.User,
    ) -> models.Task:
        return models.Task.objects.create(
            user=user_record,
            description=task.description,
            status=task.status.value,
            settings=self._create_task_settings(task.settings),
        )

    @staticmethod
    @optionally
    def _create_task_settings(settings_record: rules.Task) -> models.Task:
        return models.TaskSettings.objects.create(
            remove_task_on=settings_record.remove_task_on.value
        )
