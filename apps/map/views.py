from typing import Callable

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET
from rest_framework import viewsets, status, mixins
from rest_framework.response import Response

from apps.map import models, serializers, ui
from apps.map.adapters import controllers
from apps.map.lib import event_bus


def _error_response_for(result: ui.APIErrorResult) -> Response:
    return Response(
        dict(type=result.type),
        status=result.status_code,
        exception=True,
    )


def _error_result_of(
    error: Exception,
    as_result: Callable[tuple[str, ...], ui.APIErrorResult],
) -> ui.APIErrorResult:
    if not isinstance(error, ExceptionGroup):
        raise error from error

    result = as_result(tuple(
        type(error).__name__ for error in error.exceptions
    ))

    if result is None:
        raise error from error

    return result


@login_required
@require_GET
def map_(request: HttpRequest) -> HttpResponse:
    return render(request, "map/map.html")


class TaskViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = models.Task.objects.all()
    serializer_class = serializers.TaskSerializer

    lookup_field = "id"

    def handle_exception(self, error: Exception) -> Response:
        super().handle_exception(error)

        result = _error_result_of(error, ui.tasks.as_result)

        if result.status_code == status.HTTP_401_UNAUTHORIZED:
            self.permission_denied(self.request)

        return _error_response_for(result)


event_bus.add_event(controllers.users.on_is_registred, "user_is_registered")
