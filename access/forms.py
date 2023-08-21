from django.forms import ModelForm
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from tasks.models import User


class UserLoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ("name", "password")


class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("name", "email", "password1", "password2")


class RestoringAccessByNameForm(ModelForm):
    class Meta:
        model = User
        fields = ("name", )
        validate_unique = False


class RestoringAccessByEmailForm(ModelForm):
    class Meta:
        model = User
        fields = ("email", )
        validate_unique = False
