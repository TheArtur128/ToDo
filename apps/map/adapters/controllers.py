from act import val, original_of
from rest_framework.request import Request

from apps.map.adapters import config, repos, services
from apps.map.core import cases


@val
class users:
    def on_is_registred(id: int) -> repos.User:
        user = cases.users.on_is_registred(
            id,
            config.first_user_map_name,
            user_repo=repos.django_orm_users,
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
    ) -> repos.Task:
        task = cases.tasks.add(
            top_map_id,
            description,
            x,
            y,
            user_repo=repos.django_orm_case_tasks.Users(request),
            top_map_repo=repos.django_orm_case_tasks.top_maps,
            task_repo=repos.django_orm_case_tasks.tasks,
            uow=repos.django_orm_uow,
            service=services.tasks,
        )

        return original_of(task)
