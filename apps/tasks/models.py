from django.db import models

from apps.tasks.lib import mixins


class _Positionable(models.Model):
    x = models.PositiveIntegerField()
    y = models.PositiveIntegerField()

    class Meta:
        abstract = True


class Task(mixins.Visualizable, _Positionable):
    class Status(models.IntegerChoices):
        active = (1, "active")
        done = (2, "done")
        failed = (3, "failed")

    user = models.ForeignKey(
        "User",
        on_delete=models.CASCADE,
        related_name="tasks",
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
        return self.id
