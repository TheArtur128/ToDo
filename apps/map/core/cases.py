from typing import Callable

from act import val, struct

from apps.map.core import rules


@val
class users:
    @struct
    class UserRepo[ID: int]:
        user_of: Callable[ID, rules.User]
        saved: Callable[rules.User, rules.User]

    def on_is_registred(
        id: int,
        first_user_map_name: str,
        *,
        user_repo: UserRepo,
    ) -> rules.User:
        user = user_repo.user_of(id)

        if user is not None:
            return user

        user = rules.users.created_with(id, first_user_map_name)

        return user_repo.saved(user)
