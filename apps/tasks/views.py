from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from apps.tasks.adapters import controllers
from apps.tasks.lib import event_bus


@login_required
@require_GET
def index(request: HttpRequest) -> HttpResponse:
    return render(request, "tasks/index.html")


event_bus.add_event(controllers.users.on_is_registred, "user_is_registered")
