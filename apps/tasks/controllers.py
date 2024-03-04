from act import val

from apps.tasks.adapters import repos
from apps.tasks.core import cases


@val
class users:
    def on_is_registred(id: int) -> repos.User:
        return cases.users.on_is_registred(
            id,
            user_repo=repos.django_orm_users,
        )
