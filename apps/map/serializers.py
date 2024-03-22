from rest_framework import serializers

from apps.map import models
from apps.map.adapters import controllers


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Task
        fields = ["id", "root_map_id", "description", "x", "y"]

    root_map_id = serializers.IntegerField(read_only=True, source="root_map.id")

    def create(self, validated_data: dict) -> models.Task:
        return controllers.tasks.add(
            self._context["request"],
            validated_data["root_map"]["id"],
            validated_data["description"],
            validated_data["x"],
            validated_data["y"],
        )

    def update(self, validated_data: dict, task: models.Task) -> models.Task:
        raise NotImplementedError("In the near future")
