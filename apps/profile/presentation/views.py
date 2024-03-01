from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.views.decorators.http import require_GET

from apps.profile.presentation import ui
from apps.profile.lib import renders


@login_required
@require_GET
def profile(request: HttpRequest) -> HttpResponse:
    return renders.rendered(ui.profile.page_of(request.user), request)
