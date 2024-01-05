from typing import Callable

from act import val, A, U

from apps.tasks import rules


@val
class users:
    def create_for(
        account: A,
        *,
        user_of: Callable[[A, rules.users.default_task_settings], U],
    ) -> U:
        return user_of(account, rules.users.default_task_settings)
