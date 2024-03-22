from typing import Optional, Container

from act import val, type
from rest_framework import status


first_user_map_name = "Main"


APIErrorResult = type(status_code=int, type=Optional[str])


@val
class tasks:
    def as_result(errors: Container) -> Optional[APIErrorResult]:
        if "NoCurrentUser" in errors:
            return APIErrorResult(status.HTTP_401_UNAUTHORIZED, None)

        if "NoTopMap" in errors or "DeniedAccessToTopMap" in errors:
            return APIErrorResult(status.HTTP_404_NOT_FOUND, "NoTopMap")
