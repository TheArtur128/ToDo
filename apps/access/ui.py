from typing import Any, Optional

from act import val, type
from django.urls import reverse

from apps.access import errors, types_, lib


User = type(name=types_.Username, email=types_.Email)


@val
class profile:
    def page_of(user: User) -> lib.ui.LazyPage:
        context = dict(name=user.name, email=lib.half_hidden(user.email, 4))

        return lib.ui.LazyPage("access/profile.html", context)


@val
class registration:
    @val
    class opening:
        def error_message_of(error: Any, user: User) -> Optional[str]:
            if isinstance(error, errors.UserExists):
                return f"User \"{user.name}\" already exists"
            elif isinstance(error, errors.EmailConfirmation):
                return "Make sure you entered your email correctly"

    @val
    class completion:
        def error_message_of(error: Any, email: types_.Email) -> Optional[str]:
            if isinstance(error, errors.UserExists):
                return (
                    f"User registration has already been completed. "
                    f"Login <a href=\"{reverse("access:sign-in")}\">here<a/>"
                )
