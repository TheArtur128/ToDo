from secrets import token_urlsafe
from smtplib import SMTPException
from typing import Optional

from act import bad, of, ok, bad, Union
from django.core.cache import caches
from django.core.mail import send_mail
from django.http import HttpRequest
from django.urls import reverse

from tasks.models import User


def open_authorization_port_for(email: str, *, request: HttpRequest) -> bool:
    token = token_urlsafe(64)
    authorization_port_link = request.build_absolute_uri(
        reverse(
            "access:authorize",
            args=[token]))

    text_message = f"Follow this link to login: {authorization_port_link}"
    html_message = render_to_string(
        "mails/authorization.html",
        dict(link=authorization_port_link))

    send_result = send_mail(
        subject="Authorization",
        message=plain_text,
        html_message=html_message,
        recipient_list=[email],
        fail_silently=True)

    if send_result == 1:
        caches['emails-to-confirm'].set(token, email)

    return send_result == 1



