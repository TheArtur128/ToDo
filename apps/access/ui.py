from act import val, type

from apps.access import types_, lib


User = type(name=types_.Username, email=types_.Email)


@val
class profile:
    def page_of(user: User) -> lib.ui.LazyPage:
        context = dict(name=user.name, email=lib.half_hidden(user.email, 4))

        return lib.ui.LazyPage("access/profile.html", context)
