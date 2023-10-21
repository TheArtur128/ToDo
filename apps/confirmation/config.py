from act import name_enum_of


type Subject = str
type Method = str


@name_enum_of
class subjects:
    authorization: Subject
    registration: Subject
    access_recovery: Subject


@name_enum_of
class methods:
    email: Method
