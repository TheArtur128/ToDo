from act import val, Unia

from apps.tasks.adapters import models
from apps.tasks.core import rules


type TaskSettings = models.TaskSettings


@val
class task_settings:
    def create_defaut() -> Unia[TaskSettings, rules.default_new_task_settings]:
        return models.TaskSettings.objects.create()
