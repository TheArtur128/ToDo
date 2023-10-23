from typing import Any, TypeVar

from django.forms import Form


type ErrorMessage = str
type Annotation = Any

type URL = str
type Email = str
type Hash = str

type ID = str
type Token = str
type Name = str
type Password = str
type PasswordHash = str


FormT = TypeVar("_FormT", bound=Form)
