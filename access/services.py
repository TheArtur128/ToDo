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
                    "access:authorize",
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


def recover_access_by_name(name: str, *, request: HttpRequest) -> Union[
    ok[str],
    bad[str],
]:
    user = User.objects.filter(name=request.POST['name']).first()

    return (
        bad("There is no user with this name.")
        if user is None
        else recover_access_by_email(user.gmail, request=request)
    )


def recover_access_by_email(email: str, *, request: HttpRequest) -> Union[
    ok[str],
    bad[str],
]:
    result = account_activation_by(email, request=request)

    return (
        ok("Follow the link in the email you just received to recover access.")
        if not of(bad, result)
        else result
    )
