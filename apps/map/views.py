from typing import Optional

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET
from rest_framework import viewsets, status, exceptions
from rest_framework.response import Response

from apps.map import models, serializers, ui
from apps.map.adapters import controllers
from apps.map.lib import event_bus


def _error_response_for(result: ui.APIErrorResult) -> Response:
    return Response(
        dict(detail=result.type),
        status=result.status_code,
        exception=True,
    )


def _error_result_of(
    error: Exception,
    as_result: ui.APIErrorResultFactory[tuple[str, ...]],
) -> Optional[ui.APIErrorResult]:
    if not isinstance(error, ExceptionGroup):
        return None

    return as_result(tuple(
        type(error).__name__ for error in error.exceptions
    ))


@login_required
@require_GET
def map_(request: HttpRequest) -> HttpResponse:
    return render(request, "map/map.html")


class TaskViewSet(viewsets.ModelViewSet):
    queryset = models.Task.objects.all()
    serializer_class = serializers.TaskSerializer

    lookup_field = "id"

    def handle_exception(self, error: Exception) -> Response:
        result = _error_result_of(error, ui.tasks.as_result)

        if result is not None:
            if result.status_code == status.HTTP_401_UNAUTHORIZED:
                return super().handle_exception(exceptions.NotAuthenticated())

            return _error_response_for(result)

        return super().handle_exception(error)


event_bus.add_event(controllers.users.on_is_registred, "user_is_registered")
