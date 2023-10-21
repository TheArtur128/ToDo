from typing import Callable, Optional

from act import struct, obj, contextual, P, H, E, U, C, I, N, V, A, D, X, L


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
        is_method_correct: Callable[P, bool],
    ) -> bool:
        return is_subject_correct(port) and is_method_correct(port)

    def open_for(
        port: P,
        user_id: U,
        *,
        generate_activation_code: Callable[[], C],
        endpoint_for: Callable[[P, U, C], E],
        place_to_activate: Callable[E, L],
        sending_of: Callable[E, Callable[L, N]],
        save: Callable[E, V],
    ) -> contextual[Opening[N, V], C]:
        activation_code = generate_activation_code()

        endpoint = endpoint_for(port, user_id, activation_code)
        activation_place = place_to_activate(endpoint)

        send_to_user = sending_of(endpoint)

        sending_result = send_to_user(activation_place)
        saving_result = save(endpoint)

        opening = endpoint.Opening(sending_result, saving_result)

        return contextual(opening, activation_place)

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
    ) -> Optional[contextual[D, P]]:
        endpoint = endpoint_of(endpoint_id)

        saved_activation_code = saved_activation_code_of(endpoint)

        if not are_matched(input_activation_code, saved_activation_code):
            return None

        handle = contextualized(handling_of(endpoint))
        payload = handle(user_id_of(endpoint))

        deletion = delete(endpoint)

        return contextual(deletion, payload)
