from typing import Callable, Optional

from act import struct, obj, P, H, E, U, C, I, N, V, A, D, X


@obj.of
class endpoint:
    @struct
    class Opening[N, V]:
        sending: N
        saving: V

    @struct
    class Result[P, D]:
        payload: P
        deletion: D

    def open_for(
        port: P,
        user_id: U,
        *,
        generate_activation_code: Callable[[], C],
        endpoint_for: Callable[[P, U, C], E],
        send_access_of: Callable[E, N],
        save: Callable[E, V],
    ) -> Opening[N, V]:
        activation_code = generate_activation_code()

        endpoint = endpoint_for(port, user_id, activation_code)

        sending_result = send_access_of(endpoint)
        saving_result = save(endpoint)

        return endpoint.Opening(sending_result, saving_result)

    def activate_by(
        endpoint_id: I,
        *,
        input_activation_code: A,
        endpoint_of: Callable[I, E],
        saved_activation_code_of: Callable[E, X],
        are_matched: Callable[[A, X], bool],
        handling_of: Callable[E, H],
        contextualized: Callable[H, Callable[U, P]],
        user_id_of: Callable[E, U],
        delete: Callable[E, D],
    ) -> Optional[Result[P, D]]:
        endpoint = endpoint_of(endpoint_id)

        saved_activation_code = saved_activation_code_of(endpoint)

        if not are_matched(input_activation_code, saved_activation_code):
            return None

        handle = contextualized(handling_of(endpoint))
        payload = handle(user_id_of(endpoint))

        deletion = delete(endpoint)

        return endpoint.Result(payload, deletion)
