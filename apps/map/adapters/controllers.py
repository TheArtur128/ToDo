from functools import partial

from act import val, original_of, tmap, out
from django.db.models.query import QuerySet
from django.http import HttpRequest

from apps.map import models, ui
from apps.map.adapters import config, repos, services, uows, sculptures
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
        request: HttpRequest,
        top_map_id: int,
        description: str,
        status_code: int,
        x: int,
        y: int,
    ) -> models.Task:
        task = cases.tasks.add(
            top_map_id,
            description,
            status_code,
            x,
            y,
            user_repo=repos.DjangoOrmCurrentUsers(request),
            top_map_repo=repos.django_orm_task_case.top_maps,
            task_repo=repos.django_orm_task_case.Tasks(),
            uow=uows.django_orm,
            service=services.tasks,
        )

        return original_of(task)

    _raw_on_top_map_with_id = partial(
        cases.tasks.on_top_map_with_id,
        top_map_repo=repos.django_orm_task_case.top_maps,
    )

    def on_top_map_with_id(top_map_id: int) -> (
        "QuerySet[models.Task, models.Task]"
    ):
        return tasks._raw_on_top_map_with_id(top_map_id).query_set

    def update(
        task_record: models.Task,
        *,
        request: HttpRequest,
        description: str,
        status_code: int,
        x: int,
        y: int,
    ) -> models.Task:
        task = cases.tasks.update_by_id(
            task_id=task_record.id,
            description=description,
            status_code=status_code,
            x=x,
            y=y,
            tasks=repos.django_orm_task_case.Tasks(task_record),
            users=repos.django_orm_task_case.Users(request),
            uow=uows.django_orm,
        )

        task_record = original_of(out(task))
        assert task_record is not None

        return task_record

    @val
    class renderable:
        def on_top_map_with_id(top_map_id: int) -> tuple[ui.Task, ...]:
            return tmap(
                sculptures.renderable.task_of,
                tasks._raw_on_top_map_with_id(top_map_id).query_set,
            )


@val
class top_maps:
    def get_all(
        request: HttpRequest,
    ) -> "QuerySet[models.MapTop, models.MapTop]":
        users = repos.DjangoOrmCurrentUsers(request)
        top_maps = cases.top_maps.get_all(user_repo=users)

        return top_maps.query_set
