from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from tasks.models import User


class UserLoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ("username", "password")


class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("name", "email", "password1", "password2")
