from typing import Callable

from act import val, P, E, I, A


@val
class endpoint:
    def open_by(
        endpoint_id: I,
        *,
        endpoint_of: Callable[I, E],
        access_to_activate: Callable[E, A],
    ) -> A:
        return access_to_activate(endpoint_of(endpoint_id))

    def activate_by(
        endpoint_id: I,
        *,
        endpoint_of: Callable[I, E],
        payload_of: Callable[E, P]
    ) -> P:
        return payload_of(endpoint_of(endpoint_id))
