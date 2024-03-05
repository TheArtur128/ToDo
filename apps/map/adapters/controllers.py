from act import val

from apps.map.adapters import repos
from apps.map.core import cases


@val
class users:
    def on_is_registred(id: int) -> repos.User:
        return cases.users.on_is_registred(
            id,
            user_repo=repos.django_orm_users,
        )
