from act import val

from apps.tasks import adapters, cases, lib
from apps.tasks.types_ import Username, Email, Password


type User = lib.User


@val
class users:
    def create(name: Username, email: Email, password: Password) -> User:
        account = adapters.Account(name=name, email=email, password=password)
        user_of = adapters.user_creation.user_of

        return cases.users.create_for(account, user_of=user_of)
