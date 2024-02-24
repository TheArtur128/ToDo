from act import val
from django import forms


@val
class _user_form_fileds:
    name = forms.CharField(
        strip=True,
        widget=forms.TextInput(attrs=dict(autocomplete="username"))
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs=dict(autocomplete="email"))
    )

    password = forms.CharField(
        strip=True,
        widget=forms.PasswordInput(attrs=dict(autocomplete="current-password")),
    )

    new_password = forms.CharField(
        strip=True,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )

    password_to_repeat = forms.CharField(
        strip=True,
        widget=forms.PasswordInput
    )


class UserLoginForm(forms.Form):
    name = _user_form_fileds.name
    password = _user_form_fileds.password


class UserRegistrationForm(forms.Form):
    name = _user_form_fileds.name
    email = _user_form_fileds.email
    new_password = _user_form_fileds.new_password
    password_to_repeat = _user_form_fileds.password_to_repeat


class _PasswordConfirmationForm(forms.Form):
    new_password = _user_form_fileds.new_password
    password_to_repeat = _user_form_fileds.password_to_repeat


class RestoringAccessByNameForm(_PasswordConfirmationForm):
    name = _user_form_fileds.name


class RestoringAccessByEmailForm(_PasswordConfirmationForm):
    email = _user_form_fileds.email
