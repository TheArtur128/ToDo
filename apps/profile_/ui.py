from typing import Optional

from act import val, type

from apps.profile_ import lib


User = type(name=str, email=str)


@val
class profile:
    def page_of(
        user: User,
        previous_map_id: Optional[int] = None,
    ) -> lib.ui.LazyPage:
        context = dict(
            name=user.name,
            email=lib.half_hidden(user.email, 4),
            previous_map_id=previous_map_id,
        )

        return lib.ui.LazyPage("profile_/profile.html", context)
