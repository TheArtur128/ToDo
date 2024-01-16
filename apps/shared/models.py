from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)
from django.db.models import (
    Model, CASCADE, PositiveIntegerField, DateTimeField, BooleanField,
    CharField, EmailField, ManyToManyField, ForeignKey, PROTECT,
    OneToOneField, IntegerChoices, IntegerField, DurationField, SET_NULL
)


__all__ = ("TaskSettings", "Zone", "Task", "User")


class _VisualizableMixin:
    def __repr__(self) -> str:
        return f"{type(self).__name__}({self})"


class Space(_VisualizableMixin, Model):
    name = CharField(max_length=64, default=None, null=True, blank=True)
    user = ForeignKey("User", on_delete=CASCADE, related_name="spaces")
    user_x = PositiveIntegerField()
    user_y = PositiveIntegerField()

    next = OneToOneField(
        "self",
        on_delete=CASCADE,
        default=None,
        null=True,
        blank=True,
    )

    def __str__(self) -> str:
        return f"{self.id}: {self.name}"


class _Positionable(Model):
    class Meta:
        abstract = True

    space = ForeignKey(Space, on_delete=CASCADE)
    x = PositiveIntegerField()
    y = PositiveIntegerField()


class Task(_VisualizableMixin, _Positionable):
    class Status(IntegerChoices):
        active = (1, "active")
        done = (2, "done")
        failed = (3, "failed")

    class Color(IntegerChoices):
        first = (1, "first")
        second = (2, "second")
        third = (3, "third")
        fourth = (4, "fourth")
        fifth = (5, "fifth")
        sixth = (6, "sixth")

    description = CharField(max_length=128)
    status = IntegerField(choices=Status.choices, default=Status.active)
    settings = OneToOneField(
        "TaskSettings",
        on_delete=SET_NULL,
        default=None,
        null=True,
        blank=True,
    )

    color = IntegerField(choices=Color.choices)
    is_hidden = BooleanField(default=False)

    subspace = OneToOneField(
        Space,
        on_delete=SET_NULL,
        related_name="root",
        default=None,
        null=True,
        blank=True,
    )

    def __str__(self) -> str:
        return f"{self.id}: {self.description}"


class TaskSettings(_VisualizableMixin, Model):
    remove_on = IntegerField(
        choices=Task.Status.choices,
        default=Task.Status.done,
        null=True,
    )

    def __str__(self) -> str:
        return str(self.id)


class TaskEvent(_VisualizableMixin, Model):
    settings = ForeignKey(
        TaskSettings, on_delete=CASCADE, related_name="events"
    )

    activation_time = DateTimeField(default=None, null=True, blank=True)
    repetition_time = DurationField(default=None, null=True, blank=True)

    new_status = IntegerField(choices=Task.Status.choices, default=None, null=True)
    new_is_hidden = BooleanField(default=None, null=True, blank=True)

    is_deleter = BooleanField(default=False, blank=True)

    x_vector = IntegerField(default=0, blank=True)
    y_vector = IntegerField(default=0, blank=True)

    task_to_add = OneToOneField(
        Task,
        on_delete=SET_NULL,
        default=None,
        null=True,
        blank=True,
    )


class Zone(_VisualizableMixin, _Positionable):
    width = PositiveIntegerField()
    height = PositiveIntegerField()
    tasks = ManyToManyField("Task", related_name="zones")
    settings = OneToOneField(
        TaskSettings,
        on_delete=SET_NULL,
        default=None,
        null=True,
        blank=True,
    )

    def __str__(self) -> str:
        return str(self.id)


class CustomUserManager(BaseUserManager):
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


class User(_VisualizableMixin, AbstractBaseUser, PermissionsMixin):
    name = CharField(max_length=128, unique=True)
    email = EmailField(max_length=154, unique=True)
    password = CharField(max_length=128)
    is_active = BooleanField(default=True)
    is_staff = BooleanField(default=False)
    is_superuser = BooleanField(default=False)

    tasks = ManyToManyField(Task, blank=True)
    default_settings = OneToOneField(TaskSettings, on_delete=PROTECT)

    USERNAME_FIELD = "name"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ("email", "password")

    objects = CustomUserManager()

    def has_module_perms(self, label) -> bool:
        return self.is_superuser and self.is_staff and self.is_active

    def __str__(self) -> str:
        return self.name
