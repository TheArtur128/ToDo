from typing import Iterable

from act import val, Special, Unia, type

from apps.map import models
from apps.map.core import rules
from apps.map.adapters import sculptures


@val
class tasks:
    def is_in(maps: Iterable[rules.TopMap], map: rules.TopMap) -> bool:
        assert isinstance(maps, sculptures.QuerySetSculpture)

        return maps.query_set.filter(id=map.id).exists()

    def add_to(
        tasks: Special[
            sculptures.QuerySetSculpture[
                models.Task,
                rules.Task,
                models.MapTop,
            ],
            Iterable[rules.Task],
        ],
        task: Unia[rules.Task, type(_sculpture_original=models.Task)],
    ) -> None:
        assert isinstance(tasks, sculptures.QuerySetSculpture)

        task_record = sculptures.DjangoOrmRecords(are_saved=True).task_of(
            task,
            tasks.owner.map,
        )

        task._sculpture_original = task_record
