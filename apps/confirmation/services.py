from typing import Optional, Callable

from act import obj, will, do, Do, optionally, fun, by
from act.cursors.static import e
from django.http import HttpRequest, HttpResponse

from apps.confirmation import adapters, cases
from apps.shared.types_ import Password


type Subject = adapters.Subject
type Method = adapters.Method
type SessionToken = adapters.SessionCode


@obj.of
class endpoint_activation_of:
    _can_endpoint_be_opened_of = will(cases.endpoint.can_be_opened_for)(
        is_subject_correct=adapters.is_subject_correct,
        is_method_correct=adapters.is_method_correct,
    )

    def __call__(
        subject: Subject,
        method: Method,
    ) -> Optional[Callable]:
        port = adapters.Port(subject, method)

        if not endpoint_activation_of._can_endpoint_be_opened_of(port):
            return None

        @do(optionally)
        def activate_endpoint_by(
            do: Do,
            session_token: SessionToken,
            password: Password,
            request: HttpRequest,
        ) -> HttpResponse:
            id = adapters.EndpointID(subject, method, session_token)

            result = do(cases.endpoint.activate_by)(
                id,
                input_activation_code=password,
                endpoint_of=do(adapters.endpoint_repository.get_of),
                saved_activation_code_of=fun(e.activation_code),
                are_matched=adapters.are_activation_codes_matched,
                handling_of=do(adapters.handler_repository.get_of),
                contextualized=adapters.contextualized |by| request,
                user_id_of=fun(e.user_id),
                delete=adapters.endpoint_repository.delete,
            )

            return result.value

        return activate_endpoint_by
