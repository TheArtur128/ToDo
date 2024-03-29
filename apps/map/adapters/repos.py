from typing import Optional

from act import optionally, val
from rest_framework.request import Request

from apps.map import models
from apps.map.adapters import sculptures
from apps.map.core import rules


type User = models.User
type Task = models.Task


@val
class django_orm_users:
    def user_of(id: int) -> Optional[User]:
        user_record = models.User.objects.filter(id=id).first()

        return optionally(sculptures.rules.user_of)(user_record)

    def saved(user: rules.User) -> rules.User:
        user_record = sculptures.DjangoOrmRecords(are_saved=True).user_of(user)

        return sculptures.rules.user_of(user_record)


@val
class django_orm_case_tasks:
    class Users:
        def __init__(self, request: Request) -> None:
            self.__request = request

        def get_current(self) -> Optional[rules.User]:
            return optionally(sculptures.rules.user_of)(
                models.User.objects.filter(id=self.__request.user.id).first()
            )

    @val
    class top_maps:
        def top_map_of(id: int) -> Optional[rules.TopMap]:
            top = models.MapTop.objects.filter(id=id).first()

            return optionally(sculptures.rules.top_map_of)(top)

    @val
    class tasks:
        def saved(task: rules.Task) -> rules.Task:
            return sculptures.rules.task_of(
                sculptures.DjangoOrmRecords(are_saved=True).task_of(task)
            )
