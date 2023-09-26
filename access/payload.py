User: TypeAlias = adapters.User


@transaction
def open_registration_port_for(user: User) -> URL:
    do = do(rollbackable.optionally)

    registration = core.registration_for(
        user,
        is_already_registered=adapters.user_django_orm_repository.has,
        confirmation_access_for=do(adapters.open_confirmation_port_for),
        reminder_of=adapters.user_local_repository.save,
    )

    return registration.confirmation_access


@transaction
def register_user_by(
    email: Email,
    *,
    request: HttpRequest,
) -> User:
    do = do(rollbackable.optionally)

    return core.register_user_by(
        email,
        remembered_user_by=do(adapters.user_local_repository.get_of),
        is_already_registered=adapters.user_django_orm_repository.has,
        authorized=adapters.authorized |by| request,
        saved=returnly(adapters.user_django_orm_repository.save),
    )
