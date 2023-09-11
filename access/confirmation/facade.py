def open_email_port_of(subject: Subject, *, for_: Email) -> Optional[URL]:
    return _open_port_of(
        subject,
        for_=contextual(id_groups.email, for_),
        notify=send_confirmation_mail_to,
    )
