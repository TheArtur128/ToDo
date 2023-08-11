from typing import Callable, Self

from django.contrib.auth.models import AbstractUser
from django.db.models import (
    Model, CASCADE, PositiveIntegerField, OneToOneField, BooleanField, CharField,
    ManyToManyField, ForeignKey, PROTECT
)


class Position(Model):
    x = PositiveIntegerField()
    y = PositiveIntegerField()

    def __str__(self) -> str:
        return f"{self.x}; {self.y}"


class TaskSettings(Model):
    is_removable_on_completion = BooleanField(default=True)



class Zone(Model):
    position = OneToOneField(Position, on_delete=CASCADE)
    width = PositiveIntegerField()
    height = PositiveIntegerField()
    settings = ForeignKey(TaskSettings, on_delete=PROTECT, blank=True, null=True)


class Task(Model):
    description = CharField(max_length=128)
    is_done = BooleanField(default=False)
    subtasks = ManyToManyField("self", blank=True, symmetrical=False)
    rgb_color = CharField(max_length=6)
    position = OneToOneField(Position, on_delete=CASCADE)
    settings = ForeignKey(TaskSettings, on_delete=PROTECT, blank=True, null=True)


class User(AbstractUser):
    tasks = ManyToManyField(Task, blank=True)
    zones = ManyToManyField(Zone, blank=True)
    default_settings = ForeignKey(
        TaskSettings,
        on_delete=PROTECT,
        blank=True,
        null=True,
    )
