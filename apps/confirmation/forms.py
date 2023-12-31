from django.conf import settings
from django.forms import Form, CharField


class ConfirmationForm(Form):
    __error_message = "Password must be {} characters long.".format(
        settings.CONFIRMATION_ACTIVATION_CODE_LENGTH,
    )
    __error_messages = dict(
        min_length=__error_message,
        max_length=__error_message,
    )

    token = CharField(
        min_length=settings.CONFIRMATION_ACTIVATION_CODE_LENGTH,
        max_length=settings.CONFIRMATION_ACTIVATION_CODE_LENGTH,
        error_messages=__error_messages,
    )
