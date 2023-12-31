from django.conf import settings

from apps.shared import ui, renders
from apps.shared.tools import token_generator_with
from apps.shared.views import ViewWithForm


ui = ui
renders = renders

ViewWithForm = ViewWithForm
token_generator_with = token_generator_with

base_url = settings.BASE_URL

session_code_length = settings.CONFIRMATION_SESSION_CODE_LENGTH
activation_code_length = settings.CONFIRMATION_ACTIVATION_CODE_LENGTH

activity_minutes = settings.CONFIRMATION_ACTIVITY_MINUTES
