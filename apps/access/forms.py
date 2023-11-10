from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from apps.access.input import models


class UserLoginForm(AuthenticationForm):
    class Meta:
        model = models.User
        fields = ("name", "password")


class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = models.User
        fields = ("name", "email", "password1", "password2")


class RestoringAccessByNameForm(UserCreationForm):
    class Meta:
        model = models.User
        fields = ("name", "password1", "password2")
        validate_unique = False


class RestoringAccessByEmailForm(UserCreationForm):
    class Meta:
        model = models.User
        fields = ("email", "password1", "password2")
        validate_unique = False
