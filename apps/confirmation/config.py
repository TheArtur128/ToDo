from act import namespace

from apps.confirmation import input


type Subject = str
type Method = str


@namespace
class subjects:
    authorization: Subject
    registration: Subject
    access_recovery: Subject


@namespace
class methods:
    email: Method


base_url = input.base_url

session_code_length = input.session_code_length
activation_code_length = input.activation_code_length

activity_minutes = input.activity_minutes
