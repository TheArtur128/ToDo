from typing import Optional

from shared.types import Name, Email, Password, URL


def open_registration_port(  # todo: implement
    name: Name,
    email: Email,
    password: Password,
) -> Optional[URL]:
    ...
