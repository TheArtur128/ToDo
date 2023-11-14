from django.contrib.auth import forms

from apps.access.models import User


class UserLoginForm(forms.AuthenticationForm):
    class Meta:
        model = User
        fields = ("name", "password")


class _WithPasswordErrorMessageMixin:
    error_messages = {"password_mismatch": "Password mismatch"}


class UserRegistrationForm(
    _WithPasswordErrorMessageMixin,
    forms.UserCreationForm,
):
    class Meta:
        model = User
        fields = ("name", "email", "password1", "password2")


class RestoringAccessByNameForm(
    _WithPasswordErrorMessageMixin, 
    forms.BaseUserCreationForm,
):
    class Meta:
        model = User
        fields = ("name", "password1", "password2")
        validate_unique = False


class RestoringAccessByEmailForm(
    _WithPasswordErrorMessageMixin,
    forms.BaseUserCreationForm,
):
    class Meta:
        model = User
        fields = ("email", "password1", "password2")
        validate_unique = False
