from apps.access.lib import Application


class Access(Application): ...


class UserExists(Access): ...

class NoUser(Access): ...


class Confirmation(Access): ...

class EmailConfirmation(Confirmation): ...
