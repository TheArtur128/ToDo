from apps.confirmation import config


type Subject = config.Subject
type Method = config.Method


def is_valid(subject: Subject, method: Method) -> bool:
    return subject in config.subjects.all and method in config.methods.all
