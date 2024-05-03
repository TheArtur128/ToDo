from typing import Optional

from rest_framework import serializers

from apps.map import models
from apps.map.adapters import controllers


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Task
        fields = ["id", "description", "status_code", "x", "y"]

    status_code = serializers.IntegerField(source="status", default=1)

    def __init__(
        self,
        *args,
        top_map_id: Optional[int] = None,
        **kwargs,
    ) -> None:
        self.top_map_id = top_map_id
        super().__init__(*args, **kwargs)

    def create(self, validated_data: dict) -> models.Task:
        assert self.top_map_id is not None

        return controllers.tasks.add(
            self._context["request"],
            self.top_map_id,
            validated_data["description"],
            validated_data["status"],
            validated_data["x"],
            validated_data["y"],
        )

    def update(self, task: models.Task, validated_data: dict) -> models.Task:
        return controllers.tasks.update(
            task,
            request=self._context["request"],
            description=validated_data.get("description", task.description),
            status_code=validated_data.get("status", task.status),
            x=validated_data.get("x", task.x),
            y=validated_data.get("y", task.y),
        )


class TopMapSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MapTop
        fields = ["id", "name"]
