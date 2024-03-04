from act import val, to, tmap

from apps.access.core import rules, errors
from apps.access.core.cases import authorization


user = rules.User(0, "name", "email", "password_hash")


_user_repo_base = val(
    saved=lambda u: u,
    committed=lambda u: u,
)

full_user_repo = _user_repo_base & val(
    has_named=to(True),
    has_with_email=to(True),
    get_by_email=lambda e: user & val(email=e),
    get_by_name=lambda n: user & val(name=n),
)

empty_user_repo = _user_repo_base & val(
    has_named=to(False),
    has_with_email=to(False),
    get_by_email=to(None),
    get_by_name=to(None),
)


_base_temporary_user_repo = val(saved=lambda u: u, deleted=lambda u: u)

full_temporary_user_repo = _base_temporary_user_repo & val(
    get_by=lambda email: user & val(email=email),
)

empty_temporary_user_repo = (
    _base_temporary_user_repo & val(get_by=to(None))
)


_temporary_password_hash_repo_base = val(saved_under=lambda _, h: h)

full_temporary_password_hash_repo = (
    _temporary_password_hash_repo_base & val(get_by=to("password_hash")),
)

empty_temporary_password_hash_repo = (
    _temporary_password_hash_repo_base & val(get_by=to(None)),
)


completion_service = val(authorized=lambda u: u)


def test_successful_authorization_open_using() -> None:
    service = val(is_hash_of=to(True), confirmation_page_url_of=to('url'))

    url = authorization.open_using(
        "username", "password", service=service, repo=full_user_repo,
    )
    assert url == 'url'


def test_failure_authorization_open_using() -> None:
    try:
        service = val(is_hash_of=to(True), confirmation_page_url_of=to('url'))
        authorization.open_using(
            "username", "password", service=service, repo=empty_user_repo,
        )
    except ExceptionGroup as group:
        assert tmap(type, group.exceptions) == (errors.NoUser, )

    try:
        service = val(is_hash_of=to(False), confirmation_page_url_of=to('url'))
        authorization.open_using(
            "username", "password", service=service, repo=full_user_repo,
        )
    except ExceptionGroup as group:
        assert tmap(type, group.exceptions) == (errors.IncorrectPassword, )

    try:
        service = val(is_hash_of=to(True), confirmation_page_url_of=to(None))
        authorization.open_using(
            "username", "password", service=service, repo=full_user_repo,
        )
    except ExceptionGroup as group:
        assert tmap(type, group.exceptions) == (errors.Confirmation, )
