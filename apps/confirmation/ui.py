from typing import Optional

from act import val, as_method, optionally
from django.template.loader import render_to_string

from apps.confirmation import config, forms, types_, utils


type Subject = config.Subject
type Method = config.Method


def _readable(subject: Subject) -> utils.ui.Message:
    return subject.replace('_', ' ')


@val
class activation:
    def is_valid_for(subject: Subject, method: Method) -> bool:
        return subject in config.subjects.all and method in config.methods.all

    def mail_of(
        raw_subject: Subject,
        url: types_.URL,
        token: types_.Token,
    ) -> utils.ui.Mail:
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

        return utils.ui.Mail(
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
        *,
        is_activation_failed: bool = False,
    ) -> utils.ui.LazyPage: 
        notifications = list()
        errors = list()

        if is_activation_failed:
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

        return utils.ui.LazyPage("confirmation/pages/confirmation.html", context)

    def _error_message_of(subject: Subject) -> utils.ui.Message:
        return (
            "You entered the wrong token"
            f" or the {_readable(subject)} time has expired"
        )

    def _hint_message_of(method: utils.ui.Message) -> Optional[utils.ui.Message]:
        if method == "email":
            return "The token is in the email you just received"

        return None


@val
class opening:
    failure_message: utils.ui.Message = (
        "Make sure you have entered your information correctly"
    )
