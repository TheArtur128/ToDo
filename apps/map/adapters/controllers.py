from act import val, original_of
from django.db.models.query import QuerySet
from rest_framework.request import Request

from apps.map import models
from apps.map.adapters import config, repos, services, uows
from apps.map.core import cases


@val
class users:
    def on_is_registred(id: int) -> models.User:
        user = cases.users.on_is_registred(
            id,
            config.first_user_map_name,
            user_repo=repos.django_orm_users,
            uow=uows.django_orm,
        )

        return original_of(user)


@val
class tasks:
    def add(
        request: Request,
        top_map_id: int,
        description: str,
        x: int,
        y: int,
    ) -> models.Task:
        task = cases.tasks.add(
            top_map_id,
            description,
            x,
            y,
            user_repo=repos.DjangoOrmCurrentUsers(request),
            top_map_repo=repos.django_orm_case_tasks.top_maps,
            task_repo=repos.django_orm_case_tasks.tasks,
            uow=uows.django_orm,
            service=services.tasks,
        )

        return original_of(task)

    def on_top_map_with_id(top_map_id: int) -> (
        "QuerySet[models.Task, models.Task]"
    ):
        tasks = cases.tasks.on_top_map_with_id(
            top_map_id,
            top_map_repo=repos.django_orm_case_tasks.top_maps,
        )

        return tasks.query_set


@val
class top_maps:
    def get_all(request: Request) -> "QuerySet[models.MapTop, models.MapTop]":
        users = repos.DjangoOrmCurrentUsers(request)
        top_maps = cases.top_maps.get_all(user_repo=users)

        return top_maps.query_set
