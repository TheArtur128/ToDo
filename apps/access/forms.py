from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from apps.shared.models import User


class UserLoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ("name", "password")


class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("name", "email", "password1", "password2")


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
