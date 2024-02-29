from django.contrib import auth, postgres
from django.db import models


class _VisualizableMixin:
    def __repr__(self) -> str:
        return f"{type(self).__name__}({self})"


class Space(_VisualizableMixin, models.Model):
    name = models.CharField(max_length=64, default=None, null=True, blank=True)
    user = models.ForeignKey(
        "User",
        on_delete=models.CASCADE,
        related_name="spaces",
    )
    user_x = models.PositiveIntegerField()
    user_y = models.PositiveIntegerField()

    next = models.OneToOneField(
        "self",
        on_delete=models.CASCADE,
        default=None,
        null=True,
        blank=True,
    )

    def __str__(self) -> str:
        return f"{self.id}: {self.name}"


class _Positionable(models.Model):
    space = models.ForeignKey(Space, on_delete=models.CASCADE)
    x = models.PositiveIntegerField()
    y = models.PositiveIntegerField()

    class Meta:
        abstract = True


class Task(_VisualizableMixin, _Positionable):
    class Status(models.IntegerChoices):
        active = (1, "active")
        done = (2, "done")
        failed = (3, "failed")

    class Color(models.IntegerChoices):
        first = (1, "first")
        second = (2, "second")
        third = (3, "third")
        fourth = (4, "fourth")
        fifth = (5, "fifth")
        sixth = (6, "sixth")

    description = models.CharField(max_length=128)
    status = models.IntegerField(choices=Status.choices, default=Status.active)
    settings = models.OneToOneField(
        "TaskSettings",
        on_delete=models.SET_NULL,
        default=None,
        null=True,
        blank=True,
    )

    color = models.IntegerField(choices=Color.choices)
    is_hidden = models.BooleanField(default=False)

    subspace = models.OneToOneField(
        Space,
        on_delete=models.SET_NULL,
        related_name="root",
        default=None,
        null=True,
        blank=True,
    )

    def __str__(self) -> str:
        return f"{self.id}: {self.description}"


class TaskSettings(_VisualizableMixin, models.Model):
    remove_on = models.IntegerField(
        choices=Task.Status.choices,
        default=Task.Status.done,
        null=True,
    )

    def __str__(self) -> str:
        return str(self.id)


class TaskEvent(_VisualizableMixin, models.Model):
    settings = models.ForeignKey(
        TaskSettings, on_delete=models.CASCADE, related_name="events"
    )

    activation_time = models.DateTimeField(default=None, null=True, blank=True)
    repetition_time = models.DurationField(default=None, null=True, blank=True)

    new_status = models.IntegerField(
        choices=Task.Status.choices,
        default=None,
        null=True,
    )
    new_is_hidden = models.BooleanField(default=None, null=True, blank=True)

    is_deleter = models.BooleanField(default=False, blank=True)

    x_vector = models.IntegerField(default=0, blank=True)
    y_vector = models.IntegerField(default=0, blank=True)

    task_to_add = models.OneToOneField(
        Task,
        on_delete=models.SET_NULL,
        default=None,
        null=True,
        blank=True,
    )


class Zone(_VisualizableMixin, _Positionable):
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()
    tasks = models.ManyToManyField("Task", related_name="zones")
    settings = models.OneToOneField(
        TaskSettings,
        on_delete=models.SET_NULL,
        default=None,
        null=True,
        blank=True,
    )

    def __str__(self) -> str:
        return str(self.id)


class CustomUserManager(auth.models.BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email field is required")

        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_active", True)

        return self.create_user(email, password, **extra_fields)


class User(
    _VisualizableMixin,
    auth.models.AbstractBaseUser,
    auth.models.PermissionsMixin,
):
    name = models.CharField(max_length=128, unique=True)
    email = models.EmailField(max_length=154, unique=True)
    password = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    tasks = models.ManyToManyField(Task, blank=True)
    default_settings = models.OneToOneField(TaskSettings, on_delete=models.PROTECT)

    USERNAME_FIELD = "name"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ("email", "password")

    objects = CustomUserManager()

    class Meta:
        indexes = [
            postgres.indexes.HashIndex(fields=["name"]),
            postgres.indexes.HashIndex(fields=["email"]),
        ]

    def has_module_perms(self, label) -> bool:
        return self.is_superuser and self.is_staff and self.is_active

    def __str__(self) -> str:
        return self.name
