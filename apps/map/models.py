from django.db import models

from apps.map.lib import mixins


class _Positionable(models.Model):
    x = models.PositiveIntegerField()
    y = models.PositiveIntegerField()

    class Meta:
        abstract = True


class Map(_Positionable):
    global_task_settings = models.OneToOneField(
        "TaskSettings",
        on_delete=models.SET_NULL,
        default=None,
        null=True,
        blank=True,
    )


class MapTop(models.Model):
    map = models.OneToOneField(
        Map,
        related_name="top",
        on_delete=models.CASCADE,
    )

    user = models.ForeignKey(
        "User",
        on_delete=models.CASCADE,
        related_name="maps",
    )
    name = models.CharField(max_length=128)
    next = models.OneToOneField(
        "self",
        related_name="previous",
        on_delete=models.SET_NULL,
        default=None,
        null=True,
        blank=True,
    )


class Task(mixins.Visualizable, _Positionable):
    class Status(models.IntegerChoices):
        active = (1, "active")
        done = (2, "done")
        failed = (3, "failed")

    root_map = models.ForeignKey(
        "Map",
        on_delete=models.CASCADE,
        related_name="tasks",
    )
    submap = models.OneToOneField(
        "Map",
        on_delete=models.SET_NULL,
        default=None,
        null=True,
        blank=True,
    )

    description = models.CharField(max_length=128)
    status = models.IntegerField(choices=Status.choices, default=Status.active)
    settings = models.OneToOneField(
        "TaskSettings",
        on_delete=models.SET_NULL,
        default=None,
        null=True,
        blank=True,
    )

    def __str__(self) -> str:
        return f"{self.id}: {self.description}"


class TaskSettings(mixins.Visualizable, models.Model):
    remove_task_on = models.IntegerField(choices=Task.Status.choices)

    def __str__(self) -> str:
        return str(self.id)


class User(mixins.Visualizable, models.Model):
    global_task_settings = models.OneToOneField(
        TaskSettings,
        on_delete=models.PROTECT,
    )

    def __str__(self) -> str:
        return str(self.id)
