UserData: TypeAlias = core.User


def open_confirmation_port_for(user_data: UserData) -> Optional[URL]:
    return confirmation.facade.open_port_of(
        confirmation.facade.subjects.registration,
        confirmation.facade.via.email,
        for_=user_data.email,
    )


@dataclass(unsafe_hash=True)
class Notification:
    method: confirmation.facade.Method
    resource: str


@obj.of
class local_user_data_repository:
    _config: dict[Email, UserData] = dict()

    @as_method
    def get_of(self, email: Email) -> Optional[UserData]:
        return self._config.get(email)

    @as_method
    def save(self, user_data: UserData) -> None:
        self._config[user_data.email] = user_data


@obj.of
class django_orm_user_repository:
    def has(user_data: UserData) -> bool:
        user = models.User.objects.filter(name=user_data.name).first()

        return user is None

    def saved(user_data: UserData) -> models.User:
        user = user_from(user_data)
        user.save()

        return user


def user_from(user_data: UserData) -> models.User:
    return models.User(
        name=user_data.name,
        email=user_data.email,
        password=user_data.password,
    )
