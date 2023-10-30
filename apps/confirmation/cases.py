from typing import Callable, Optional

from act import struct, obj, P, M, E, U, I, A


@obj.of
class endpoint:
    @struct
    class Opening[N, V]:
        sending: N
        saving: V

    def can_be_opened_for(
        port: P,
        *,
        is_subject_correct: Callable[P, bool],
        is_activation_method_correct: Callable[P, bool],
    ) -> bool:
        return is_subject_correct(port) and is_activation_method_correct(port)

    def open_for(
        port: P,
        user_id: U,
        *,
        endpoint_of: Callable[P, E],
        with_activation_method_sent_to_user: Callable[E, A],
        place_to_activate: Callable[A, P],
    ) -> P:
        endpoint_ = endpoint_of(port, user_id)

        return place_to_activate(with_activation_method_sent_to_user(endpoint_))

    def activate_by(
        endpoint_id: I,
        *,
        endpoint_of: Callable[[I, M], E],
        is_activated: Callable[E, bool],
        payload_of: Callable[E, P]
    ) -> Optional[P]:
        endpoint_ = endpoint_of(endpoint_id)

        return payload_of(endpoint_) if is_activated(endpoint_) else None
