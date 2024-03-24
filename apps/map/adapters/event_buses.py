from act import val

from apps.map.lib import event_bus


@val
class users:
    def sent_failed_registration_message_with(id: int) -> str:
        message = "user_registration_is_failed"
        event_bus.emit(message, id)

        return message
