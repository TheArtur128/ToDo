from typing import TypeAlias


__all__ = (
    "ErrorMessage", "Annotaton", 'URL', "Email", "Password", "PasswordHash",
    "Name"
)


ErrorMessage: TypeAlias = str
Annotaton: TypeAlias = Any

URL: TypeAlias = str
Email: TypeAlias = str
Password: TypeAlias = str
PasswordHash: TypeAlias = str

Name: TypeAlias = str
