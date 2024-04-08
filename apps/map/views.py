from typing import Optional

from django.contrib.auth.decorators import login_required
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse
from django.views.decorators.http import require_GET
from rest_framework import viewsets, status, exceptions, mixins
from rest_framework.response import Response

from apps.map import models, serializers, ui
from apps.map.adapters import controllers
from apps.map.lib import event_bus, renders


def _error_response_for(result: ui.APIErrorResult) -> Response:
    return Response(result.body, status=result.status_code, exception=True)


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
def map_view(request: HttpRequest, top_map_id: int) -> HttpResponse:
    tasks = controllers.tasks.renderable.on_top_map_with_id(top_map_id)
    page = ui.tasks.controller_page_for(tasks, top_map_id)

    return renders.rendered(page, request)


@login_required
@require_GET
def map_selection_view(request: HttpRequest) -> HttpResponse:
    maps = controllers.top_maps.get_all(request)

    return renders.rendered(ui.maps.selection_page_between(maps), request)


class _ViewSetErrorHandlingMixin:
    _api_error_result_factory: ui.APIErrorResultFactory[tuple[str, ...]]
    _api_error_result_factory = staticmethod(ui.as_result)

    def handle_exception(self, error: Exception) -> Response:
        result = _error_result_of(error, self._api_error_result_factory)

        if result is not None:
            if result.status_code == status.HTTP_401_UNAUTHORIZED:
                return super().handle_exception(exceptions.NotAuthenticated())

            return _error_response_for(result)

        return super().handle_exception(error)


class TaskViewSet(
    _ViewSetErrorHandlingMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = models.Task.objects.all()
    serializer_class = serializers.TaskSerializer

    lookup_field = "id"


class TopMapTaskViewSet(
    _ViewSetErrorHandlingMixin,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = serializers.TaskSerializer

    def get_queryset(self) -> QuerySet:
        return controllers.tasks.on_top_map_with_id(self.kwargs["top_map_id"])

    def get_serializer(self, *args, **kwargs) -> serializers.TaskSerializer:
        kwargs["top_map_id"] = self.kwargs["top_map_id"]

        return super().get_serializer(*args, **kwargs)


class TopMapViewSet(
    _ViewSetErrorHandlingMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = serializers.TopMapSerializer

    def get_queryset(self) -> QuerySet:
        return controllers.top_maps.get_all(self.request)


event_bus.add_event(controllers.users.on_is_registred, "user_is_registered")
