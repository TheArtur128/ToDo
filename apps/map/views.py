from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from apps.map.adapters import controllers
from apps.map.lib import event_bus


@login_required
@require_GET
def map_(request: HttpRequest) -> HttpResponse:
    return render(request, "map/map.html")


event_bus.add_event(controllers.users.on_is_registred, "user_is_registered")
