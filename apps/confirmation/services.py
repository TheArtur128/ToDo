from typing import Optional, Callable

from act import obj, will, do, Do, optionally
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
            id = adapters.EndpointID(subject, method, session_token, password)

            result = do(cases.endpoint.activate_by)(
                id,
                endpoint_of=adapters.endpoint_of,
                is_activated=adapters.is_activated,
                payload_of=adapters.payload_of,
            )

            return result

        return activate_endpoint_by
