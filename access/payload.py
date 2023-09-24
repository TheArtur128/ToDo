User: TypeAlias = adapters.User


def open_registration_port_for(user: User) -> Optional[URL]:
    open_confirmation_port_for = rollbackable.optionally(
        adapters.open_confirmation_port_for,
    )

    with Transaction() as get_ok:
        registration = core.registration_for(
            user,
            is_already_registered=adapters.user_django_orm_repository.has,
            confirmation_access_for=open_confirmation_port_for,
            reminder_of=adapters.user_local_repository.save,
        )

    return registration.confirmation_access if get_ok() else None


def register_user_by(
    email: Email,
    *,
    request: HttpRequest,
) -> Optional[User]:
    user_by = rollbackable.optionally(
        adapters.user_local_repository.get_of
    )

    with Transaction() as get_ok:
        user = core.register_user_by(
            email,
            remembered_user_by=user_by,
            is_already_registered=adapters.user_django_orm_repository.has,
            authorized=authorized |by| request,
            saved=returnly(adapters.user_django_orm_repository.save),
        )

    return user if get_ok() else None
