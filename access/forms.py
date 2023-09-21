from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.forms import Form, CharField

from shared.models import User


class UserLoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ("name", "password")


class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("name", "email", "password1", "password2")


class ConfirmationForm(Form):
    password = CharField(
        min_length=settings.PORT_PASSWORD_LENGTH,
        max_length=settings.PORT_PASSWORD_LENGTH,
    )


class RestoringAccessByNameForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("name", "password1", "password2")
        validate_unique = False


class RestoringAccessByEmailForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("email", "password1", "password2")
        validate_unique = False
