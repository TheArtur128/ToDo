from django.conf import settings
from django.forms import Form, CharField


class ConfirmationForm(Form):
    password = CharField(
        min_length=settings.CONFIRMATION_ACTIVATION_CODE_LENGTH,
        max_length=settings.CONFIRMATION_ACTIVATION_CODE_LENGTH,
    )
