from contextlib import AbstractContextManager
from typing import Callable, Iterable, Optional, Any

from act import val, struct, type

from apps.map.core import rules, errors
from apps.map.lib import to_raise_multiple_errors, raise_, last, exists


@val
class users:
    @struct
    class UserRepo[ID: int]:
        user_of: Callable[ID, rules.User]
        saved: Callable[rules.User, rules.User]

    def on_is_registred(
        id: int,
        first_user_map_name: str,
        *,
        user_repo: UserRepo,
    ) -> rules.User:
        user = user_repo.user_of(id)

        if user is not None:
            return user

        user = rules.users.created_with(id, first_user_map_name)

        return user_repo.saved(user)


@val
class tasks:
    UserRepo = type(get_current=Callable[[], Optional[rules.User]])
    TopMapRepo = type(top_map_of=Callable[int, Optional[rules.TopMap]])
    TaskRepo = type(saved=Callable[rules.Task, rules.Task])
    UoW = Callable[TaskRepo, AbstractContextManager]

    @struct
    class Service:
        is_in: Callable[[Iterable[rules.TopMap], rules.TopMap], bool]
        add_to: Callable[[Iterable[rules.Task], rules.Task], Any]

    @to_raise_multiple_errors
    def add(
        top_map_id: int,
        description: str,
        x: int,
        y: int,
        *,
        user_repo: UserRepo,
        top_map_repo: TopMapRepo,
        task_repo: TaskRepo,
        uow: UoW,
        service: Service,
    ) -> rules.Task:
        current_user = user_repo.get_current()
        yield from exists(current_user, errors.NoCurrentUser())

        top_map = top_map_repo.top_map_of(top_map_id)
        yield from exists(current_user, errors.NoTopMap())

        yield raise_

        if not service.is_in(current_user.maps, top_map):
            yield last(errors.DeniedAccessToTopMap())

        with uow(task_repo):
            task = task_repo.saved(rules.tasks.created_with(description, x, y))
            service.add_to(top_map.tasks, task)

        return task
