from act import val, type

from apps.profile import lib


User = type(name=str, email=str)


@val
class profile:
    def page_of(user: User) -> lib.ui.LazyPage:
        context = dict(name=user.name, email=lib.half_hidden(user.email, 4))

        return lib.ui.LazyPage("profile/profile.html", context)
