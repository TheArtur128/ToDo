from act import val, type

from apps.access import types_, utils


User = type(name=types_.Username, email=types_.Email)


@val
class profile:
    def page_of(user: User) -> utils.ui.LazyPage:
        context = dict(name=user.name, email=utils.half_hidden(user.email, 4))

        return utils.ui.LazyPage("access/profile.html", context)
