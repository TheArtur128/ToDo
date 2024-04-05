from rest_framework import serializers

from apps.map import models
from apps.map.adapters import controllers


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Task
        fields = ["id", "description", "x", "y"]

    def __init__(self, *args, top_map_id: int, **kwargs) -> None:
        self.top_map_id = top_map_id
        super().__init__(*args, **kwargs)

    def create(self, validated_data: dict) -> models.Task:
        return controllers.tasks.add(
            self._context["request"],
            self.top_map_id,
            validated_data["description"],
            validated_data["x"],
            validated_data["y"],
        )

    def update(self, validated_data: dict, task: models.Task) -> models.Task:
        raise NotImplementedError("In the near future")


class TopMapSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MapTop
        fields = ["id", "name"]
