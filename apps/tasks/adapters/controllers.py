from act import val

from apps.tasks.adapters import repos
from apps.tasks.core import cases


@val
class task_settings:
    def create_defaut() -> repos.TaskSettings:
        return cases.task_settings.create_defaut(repo=repos.task_settings)
