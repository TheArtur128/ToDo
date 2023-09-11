def open_email_port_of(subject: Subject, *, for_: Email) -> Optional[URL]:
    return _open_port_of(
        subject,
        for_=contextual(id_groups.email, for_),
        notify=send_confirmation_mail_to,
    )


ViewHandler: TypeAlias = Callable[[AuthToken, HttpRequest, I], Optional[HttpResponse]]


@closing(close_port_of=close_port_of)
@obj.of
class HandlerChachRepository(Generic[I]):
    def get_of(port_id: PortID) -> ViewHandler:
        ...

    def registrate_for(port_id: PortID) -> reformer_of[ViewHandler]:
        ...
