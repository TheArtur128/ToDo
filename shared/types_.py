from typing import TypeAlias, Callable, Any

from act import via_indexer, temp


ErrorMessage: TypeAlias = str
Annotation: TypeAlias = Any

URL: TypeAlias = str
ID: TypeAlias = str
Email: TypeAlias = str
Password: TypeAlias = str
PasswordHash: TypeAlias = str

Name: TypeAlias = str

FormT = TypeVar("_FormT", bound=Form)


@via_indexer
def RepositoryFromTo(
    key_annotation: Annotation,
    value_annotation: Annotation,
) -> temp:
    return temp(
        get_of=Callable[key_annotation, value_annotation],
        has_of=Callable[key_annotation, bool],
        create_for=Callable[key_annotation, Any],
    )


@via_indexer
def ActionOf(
    parameters_annotation: Annotation,
    return_annotation: Annotation,
) -> temp:
    return temp(__call__=Callable[parameters_annotation, return_annotation])
