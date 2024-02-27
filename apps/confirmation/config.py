from act import namespace
from django.conf import settings


type Subject = str
type Method = str


@namespace
class subjects:
    authorization: Subject
    registration: Subject
    access_recovery: Subject


@namespace
class methods:
    email: Method
    console: Method


base_url = settings.HOST
is_dev = settings.IS_DEV and settings.EMAIL_HOST is None

session_code_length = settings.CONFIRMATION_SESSION_CODE_LENGTH
activation_code_length = settings.CONFIRMATION_ACTIVATION_CODE_LENGTH

activity_minutes = settings.CONFIRMATION_ACTIVITY_MINUTES
