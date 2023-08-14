from django.shortcuts import render
from django.views.decorators.http import require_GET


def index(request: HttpRequest) -> HttpResponse:
    return render(request, 'index.html')
