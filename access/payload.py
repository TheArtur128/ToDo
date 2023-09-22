UserData = adapters.UserData


def open_registration_port_for(user_data: UserData) -> Optional[URL]:
    open_confirmation_port_for = rollbackable.optionally(
        adapters.open_confirmation_port_for,
    )

    with Transaction(open_confirmation_port_for) as get_ok:
        confirmation_page_url = core.open_registration_port_for(
            user_data,
            already_have=adapters.django_orm_user_repository.has,
            open_confirmation_port_for=open_confirmation_port_for,
            remember=adapters.local_user_data_repository.save,
        )

    return confirmation_page_url if get_ok() else None


def registered_user_by(
    email: Email,
    request: HttpRequest,
) -> Optional[models.User]:
    user_data = adapters.local_user_data_repository.get_of(email)

    if user_data is None:
        return None

    return core.registrate(
        user_data,
        already_have=adapters.django_orm_user_repository.has,
        authorized=user_from |then>> returnly(auth.login |to| request),
        saved=django_orm_user_repository.saved,
    )
