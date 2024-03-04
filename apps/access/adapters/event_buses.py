from act import val

from apps.access.lib import event_bus


@val
class registration:
    def send_user_is_registered(id: int) -> None:
        event_bus.emit("user_is_registered", id)
