from typing import Callable, Optional, Container

from act import type
from rest_framework import status


first_user_map_name = "Main"


APIErrorResult = type(status_code=int, type=Optional[str])

type APIErrorResultFactory[ValuesT: Container] = (
    Callable[ValuesT, Optional[APIErrorResult]]
)


def as_result(errors: Container) -> Optional[APIErrorResult]:
    if "NoCurrentUser" in errors:
        return APIErrorResult(status.HTTP_401_UNAUTHORIZED, None)

    if "NoTopMap" in errors or "DeniedAccessToTopMap" in errors:
        return APIErrorResult(status.HTTP_404_NOT_FOUND, "NoTopMap")
