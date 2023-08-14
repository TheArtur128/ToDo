from secrets import token_urlsafe
from smtplib import SMTPException
from typing import Optional

from act import bad, of, ok, bad, Union
from django.core.cache import caches
from django.core.mail import send_mail
from django.http import HttpRequest
from django.urls import reverse

from tasks.models import User


def account_activation_by(email: str, *, request: HttpRequest) -> Optional[
    bad[str]
]:
    token = token_urlsafe(64)

    try:
        send_mail(
            "Authorization",
            "Follow this link to authorize:\n{}\n\n{}".format(
                request.build_absolute_uri(reverse(
                    "accounts:authorize",
                    args=[token],
                )),
                "Don't share this link with anyone.",
            ),
            None,
            [email],
        )
    except SMTPException:
        return bad('Make sure the email is correct or try again after a while.')

    caches['emails-to-confirm'].set(token, email)
