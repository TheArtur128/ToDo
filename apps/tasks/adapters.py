from act import type, val

from apps.tasks import rules, lib
from apps.tasks.types_ import Username, Email, Password


type User = lib.User

Account = type(name=Username, email=Email, password=Password)


@val
class user_creation:
    def user_of(
        account: Account,
        default_task_settings: rules.users.default_task_settings,
    ) -> User:
        remove_on = default_task_settings.remove_on.value
        settings = lib.TaskSettings.objects.create(remove_on=remove_on)

        return lib.User.objects.create(
            name=account.name,
            email=account.email,
            password=account.password,
            default_settings=settings,
        )
