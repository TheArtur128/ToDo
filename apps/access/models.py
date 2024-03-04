from django.contrib import auth, postgres
from django.db import models

from apps.access.lib import mixins


class _CustomUserManager(auth.models.BaseUserManager):
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
    mixins.Visualizable,
    auth.models.AbstractBaseUser,
    auth.models.PermissionsMixin,
):
    name = models.CharField(max_length=128, unique=True)
    email = models.EmailField(max_length=154, unique=True)
    password = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = "name"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ("email", "password")

    objects = _CustomUserManager()

    class Meta:
        indexes = [
            postgres.indexes.HashIndex(fields=["name"]),
            postgres.indexes.HashIndex(fields=["email"]),
        ]

    def has_module_perms(self, label) -> bool:
        return self.is_superuser and self.is_staff and self.is_active

    def __str__(self) -> str:
        return self.name
