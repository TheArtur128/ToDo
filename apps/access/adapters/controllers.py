from act import val, will

from django.http import HttpRequest

from apps.access.adapters import services, repos, models
from apps.access.core import cases, types_


type User = models.User


@val
class registration:
    open_using = will(cases.registration.open_using)(
        service=services.registration.opening,
        repo=repos.user_django_orm_repository,
        temporary_repo=repos.user_redis_repository,
    )

    def complete_by(email: types_.Email, request: HttpRequest) -> User:
        return cases.registration.complete_by(
            email,
            service=services.registration.Completion(request),
            repo=repos.user_django_orm_repository,
            temporary_repo=repos.user_redis_repository,
        )


@val
class authorization:
    open_using = will(cases.authorization.open_using)(
        service=services.authorization.opening,
        repo=repos.user_django_orm_repository,
    )

    def complete_by(email: types_.Email, request: HttpRequest) -> User:
        return cases.authorization.complete_by(
            email,
            service=services.authorization.Completion(request),
            repo=repos.user_django_orm_repository,
        )


@val
class access_recovery:
    open_using_name = will(cases.access_recovery.open_using)(
        service=services.access_recovery.opening,
        user_repo=repos.access_recovery.name_user_repository,
        password_hash_repo=repos.redis_password_hash_repository,
    )

    open_using_email = will(cases.access_recovery.open_using)(
        service=services.access_recovery.opening,
        user_repo=repos.access_recovery.email_user_repository,
        password_hash_repo=repos.redis_password_hash_repository,
    )

    def complete_by(email: types_.Email, request: HttpRequest) -> User:
        return cases.access_recovery.complete_by(
            email,
            service=services.access_recovery.Completion(request),
            user_repo=repos.user_django_orm_repository,
            password_hash_repo=repos.redis_password_hash_repository,
        )
