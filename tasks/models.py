from django.contrib.auth.models import AbstractUser
from django.db.models import (
    Model, CASCADE, PositiveIntegerField, OneToOneField, BooleanField,
    CharField, ManyToManyField, ForeignKey, PROTECT
)


__all__ = ("Position", "TaskSettings", "Zone", "Task", "User")


class _VisualizableMixin:
    def __repr__(self) -> str:
        return f"{type(self).__name__}({self})"


class Position(_VisualizableMixin, Model):
    x = PositiveIntegerField()
    y = PositiveIntegerField()

    def __str__(self) -> str:
        return f"id={self.id}, x={self.x}, y={self.y}"


class TaskSettings(_VisualizableMixin, Model):
    is_removable_on_completion = BooleanField(default=True)

    def __str__(self) -> str:
        return (
            f"id={self.id}, "
            f"is_removable_on_completion={self.is_removable_on_completion}"
        )


class Zone(_VisualizableMixin, Model):
    position = OneToOneField(Position, on_delete=CASCADE)
    width = PositiveIntegerField()
    height = PositiveIntegerField()
    settings = ForeignKey(
        TaskSettings,
        on_delete=PROTECT,
        blank=True,
        null=True,
    )

    def __str__(self) -> str:
        return (
            f"id={self.id}, "
            f"position=({self.position}), "
            f"width={self.width}, "
            f"height={self.height}"
        )


class Task(_VisualizableMixin, Model):
    description = CharField(max_length=128)
    is_done = BooleanField(default=False)
    subtasks = ManyToManyField("self", blank=True, symmetrical=False)
    rgb_color = CharField(max_length=6)
    position = OneToOneField(Position, on_delete=CASCADE)
    settings = ForeignKey(
        TaskSettings,
        on_delete=PROTECT,
        blank=True,
        null=True,
    )

    def __str__(self) -> str:
        return f"id={self.id}, is_done={self.is_done}"


class User(AbstractUser):
    tasks = ManyToManyField(Task, blank=True)
    zones = ManyToManyField(Zone, blank=True)
    default_settings = ForeignKey(
        TaskSettings,
        on_delete=PROTECT,
        blank=True,
        null=True,
    )
