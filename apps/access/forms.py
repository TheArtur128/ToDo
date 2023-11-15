from django.contrib.auth import forms
from django.forms import (
    Form, ValidationError, PasswordInput, CharField, EmailField
)

from apps.access.models import User
from apps.access.types_ import Password


_password_error_messages = dict(password_mismatch="Password mismatch")


class _PasswordConfirmationForm(Form):
    error_messages = _password_error_messages

    password1 = CharField(widget=PasswordInput, max_length=128)
    password2 = CharField(widget=PasswordInput, max_length=128)

    def clean_password2(self) -> Password:
        password1 = self.cleaned_data["password1"]
        password2 = self.cleaned_data["password2"]

        if password1 != password2:
            raise ValidationError(
                self.error_messages["password_mismatch"],
                code="password_mismatch",
            )

        return password2


class UserLoginForm(forms.AuthenticationForm):
    class Meta:
        model = User
        fields = ("name", "password")


class UserRegistrationForm(forms.UserCreationForm):
    error_messages = _password_error_messages

    class Meta:
        model = User
        fields = ("name", "email", "password1", "password2")


class RestoringAccessByNameForm(_PasswordConfirmationForm):
    name = CharField(max_length=128)


class RestoringAccessByEmailForm(_PasswordConfirmationForm):
    email = EmailField(max_length=154)
