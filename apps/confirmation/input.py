from django.conf import settings

from apps.shared import types_
from apps.shared.views import ViewWithForm
from apps.shared.tools import token_generator_with


ViewWithForm = ViewWithForm
token_generator_with = token_generator_with

type URL = types_.URL
type Token = types_.Token
type Email = types_.Email
type Password = types_.Password
type ErrorMessage = types_.ErrorMessage

base_url = settings.BASE_URL

session_code_length = settings.CONFIRMATION_SESSION_CODE_LENGTH
activation_code_length = settings.CONFIRMATION_ACTIVATION_CODE_LENGTH

activity_minutes = settings.CONFIRMATION_ACTIVITY_MINUTES
