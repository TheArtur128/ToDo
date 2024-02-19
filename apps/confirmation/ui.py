from typing import Optional, Iterable

from act import val, as_method, optionally
from django.template.loader import render_to_string

from apps.confirmation import config, forms, types_, lib


type Subject = config.Subject
type Method = config.Method


def _readable(subject: Subject) -> lib.ui.Message:
    return subject.replace('_', ' ')


@val
class activation:
    def is_valid_for(subject: Subject, method: Method) -> bool:
        return subject in config.subjects.all and method in config.methods.all

    def mail_of(
        raw_subject: Subject,
        url: types_.URL,
        token: types_.Token,
    ) -> lib.ui.Mail:
        subject = _readable(raw_subject)

        title = f"Confirm {subject}"
        message = f"Token to confirm {subject} in {url}: {token}"
        page = render_to_string(
            "confirmation/mails/to-confirm.html",
            dict(
                subject=subject,
                url=url,
                token=token,
                activity_minutes=config.activity_minutes,
            ),
        )

        return lib.ui.Mail(
            title=title,
            message=message,
            page=page,
        )

    @as_method
    def page_of(
        self,
        form: forms.ConfirmationForm,
        subject: Subject,
        method: Method,
        session_token: types_.Token,
        errors: Iterable[str],
        *,
        is_activation_failed: bool = False,
    ) -> lib.ui.LazyPage: 
        notifications = list()
        errors = list(errors)

        if is_activation_failed and len(errors) == 0:
            errors.append(self._error_message_of(subject))
        else:
            optionally(notifications.append)(self._hint_message_of(method))

        context = dict(
            subject=subject,
            readable_subject=_readable(subject),
            method=method,
            session_token=session_token,
            form=form,
            errors=(*form.errors.values(), *errors),
            notifications=notifications,
        )

        return lib.ui.LazyPage("confirmation/pages/confirmation.html", context)

    def _error_message_of(subject: Subject) -> lib.ui.Message:
        return (
            "You entered the wrong token"
            f" or the {_readable(subject)} time has expired"
        )

    def _hint_message_of(method: lib.ui.Message) -> Optional[lib.ui.Message]:
        if method == "email":
            return "The token is in the email you just received"

        return None


@val
class opening:
    failure_message: lib.ui.Message = (
        "Make sure you have entered your information correctly"
    )
