from typing import Optional

from apps.confirmation import config


type _Message = str

type Subject = config.Subject
type Method = config.Method

activity_minutes = config.activity_minutes


def is_valid(subject: Subject, method: Method) -> bool:
    return subject in config.subjects.all and method in config.methods.all


def hint_message_for(method: Method) -> Optional[_Message]:
    if method == config.methods.email:
        return "The token is in the email you just received"

    return None
