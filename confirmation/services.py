from act import do, Do, optionally, fun, by
from act.cursors.static import e
from django.http import HttpRequest, HttpResponse

from confirmation import adapters, cases
from shared.types_ import Password


type Subject = adapters.Subject
type Method = adapters.Method
type SessionToken = adapters.SessionCode


@do(optionally)
def activate_endpoint_by(
    do: Do,
    subject: Subject,
    method: Method,
    session_token: SessionToken,
    password: Password,
    request: HttpRequest,
) -> HttpResponse:
    view = adapters.EndpointView(subject, method, session_token)

    result = do(cases.endpoint.activate_by)(
        view,
        input_activation_code=password,
        endpoint_of=do(adapters.endpoint_repository.get_of),
        saved_activation_code_of=fun(e.activation_code),
        are_matched=adapters.are_activation_codes_matched,
        handling_of=do(adapters.handler_repository.get_of),
        contextualized=adapters.contextualized |by| request,
        user_id_of=fun(e.user_id),
        delete=do(adapters.endpoint_repository.delete),
    )

    return result.payload
