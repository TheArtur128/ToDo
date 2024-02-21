from typing import Any

from act import Unia


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


type Sculpture[FormT, OriginalT] = (
    Unia[FormT, type(_sculpture_original=OriginalT)]
)
