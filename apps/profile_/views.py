from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.views.decorators.http import require_GET

from apps.profile_ import ui
from apps.profile_.lib import renders


@login_required
@require_GET
def profile(request: HttpRequest) -> HttpResponse:
    previous_map_id = request.GET.get("from_map")
    page = ui.profile.page_of(request.user, previous_map_id=previous_map_id)

    return renders.rendered(page, request)
