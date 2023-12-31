from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from apps.shared.ui import LazyPage


def rendered(page: LazyPage, request: HttpRequest) -> HttpResponse:
    return render(request, page.template, page.context)
