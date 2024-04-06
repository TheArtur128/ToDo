from typing import Callable, Optional, Container, Iterable

from act import type, val
from rest_framework import status

from apps.map.lib import ui


first_user_map_name = "Main"

Map = type(id=int, name=str)
Task = type(description=str, x=int, y=int, is_done=bool)


@val
class tasks:
    def controller_page_for(tasks: Iterable[Task], map_id: int) -> ui.LazyPage:
        return ui.LazyPage("map/map.html", dict(tasks=tasks, map_id=map_id))


@val
class maps:
    def selection_page_between(maps: Iterable[Map]) -> ui.LazyPage:
        return ui.LazyPage("map/selection.html", dict(maps=maps))


APIErrorResult = type(status_code=int, type=Optional[str])

type APIErrorResultFactory[ValuesT: Container] = (
    Callable[ValuesT, Optional[APIErrorResult]]
)


def as_result(errors: Container) -> Optional[APIErrorResult]:
    if "NoCurrentUser" in errors:
        return APIErrorResult(status.HTTP_401_UNAUTHORIZED, None)

    if "NoTopMap" in errors or "DeniedAccessToTopMap" in errors:
        return APIErrorResult(status.HTTP_404_NOT_FOUND, "NoTopMap")
