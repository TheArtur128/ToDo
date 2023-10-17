from typing import TypeAlias, Any, TypeVar

from django.forms import Form


ErrorMessage: TypeAlias = str
Annotation: TypeAlias = Any

URL: TypeAlias = str
ID: TypeAlias = str
Email: TypeAlias = str
Password: TypeAlias = str
PasswordHash: TypeAlias = str
Token = str

Name: TypeAlias = str

FormT = TypeVar("_FormT", bound=Form)
