from typing import Optional, Any

from act import optionally, val, out, original_of
from django import db  # noqa: F401
from django.http import HttpRequest

from apps.map import models
from apps.map.adapters import sculptures
from apps.map.core import rules


type User = models.User
type Task = models.Task
type Tasks = "db.models.query.QuerySet[models.Task, models.Task]"


@val
class django_orm_users:
    def user_of(id: int) -> Optional[User]:
        user_record = models.User.objects.filter(id=id).first()

        return optionally(sculptures.rules.user_of)(user_record)

    def saved(user: rules.User) -> rules.User:
        user_record = sculptures.DjangoOrmRecords(are_saved=True).user_of(user)

        return sculptures.rules.user_of(user_record)


class DjangoOrmCurrentUsers:
    def __init__(self, request: HttpRequest) -> None:
        self.__request = request

    def get_current(self) -> Optional[rules.User]:
        return optionally(sculptures.rules.user_of)(
            models.User.objects.filter(id=self.__request.user.id).first()
        )

@val
class django_orm_task_case:
    @val
    class top_maps:
        def top_map_of(id: int) -> Optional[rules.TopMap]:
            top = models.MapTop.objects.filter(id=id).first()

            return optionally(sculptures.rules.top_map_of)(top)

    class Tasks:
        def __init__(self, task_record: Optional[models.Task] = None) -> None:
            self.__task = optionally(sculptures.rules.task_of)(task_record)

        def task_of(self, _: Any) -> Optional[rules.Task]:
            return self.__task

        def saved(self, task: rules.Task) -> rules.Task:
            return task

        def committed(self, task: rules.Task) -> rules.Task:
            task_record = original_of(out(task))
            assert isinstance(task_record, models.Task)

            task_record.description = task.description
            task_record.status = task.status.value
            task_record.x = task.position.x
            task_record.y = task.position.y

            task_record.save()

            return task

    class Users(DjangoOrmCurrentUsers):
        def user_having(self, task: rules.Task) -> Optional[rules.User]:
            task_record = original_of(out(task))
            assert isinstance(task_record, models.Task)

            top = out(task_record.root_map).top

            return None if top is None else top.user
