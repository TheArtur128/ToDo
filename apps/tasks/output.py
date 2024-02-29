from typing import Callable

from apps.tasks.adapters import models, controllers


create_defaut_task_settings: Callable[[], models.TaskSettings]
create_defaut_task_settings = controllers.task_settings.create_defaut
