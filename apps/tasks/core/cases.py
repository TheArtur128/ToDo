from typing import Callable

from act import val, struct

from apps.tasks.core import rules


@val
class task_settings:
    @struct
    class Repo:
        create_defaut: Callable[[], rules.default_new_task_settings]

    def create_defaut(*, repo: Repo) -> rules.default_new_task_settings:
        return repo.create_defaut()
