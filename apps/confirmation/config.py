from act import namespace


type Subject = str
type Method = str


@namespace
class subjects:
    authorization: Subject
    registration: Subject
    access_recovery: Subject


@namespace
class methods:
    email: Method
