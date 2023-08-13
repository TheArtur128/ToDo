from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)
from django.db.models import (
    Model, CASCADE, PositiveIntegerField, OneToOneField, BooleanField,
    CharField, EmailField, ManyToManyField, ForeignKey, PROTECT
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


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email field is required')

        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    name = CharField(max_length=128, unique=True)
    email = EmailField(max_length=154, unique=True)
    password = CharField(max_length=128)
    is_active = BooleanField(default=False)
    is_staff = BooleanField(default=False)
    is_superuser = BooleanField(default=False)

    tasks = ManyToManyField(Task, blank=True)
    zones = ManyToManyField(Zone, blank=True)
    default_settings = ForeignKey(
        TaskSettings,
        on_delete=PROTECT,
        blank=True,
        null=True,
    )

    USERNAME_FIELD = "name"
    REQUIRED_FIELDS = ("email", "password")

    objects = CustomUserManager()

    def has_module_perms(self, label) -> bool:
        return self.is_superuser and self.is_staff and self.is_active
