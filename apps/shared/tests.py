from act import on, to, raise_, ok
from pytest import mark

from apps.shared import lib, errors, validation


@mark.parametrize("token_length", [*range(10), 32, 64, 128, 1024, 2069])
def test_token_generator_with(token_length: int) -> None:
    generate = lib.token_generator_with(length=token_length)

    assert len(generate()) == token_length
    assert len(generate()) == token_length
    assert len(generate()) == token_length


def test_half_hidden() -> None:
    assert lib.half_hidden("12345", 3) == "#####"
    assert lib.half_hidden("1234567890", 3) == "123####890"
    assert lib.half_hidden("1234567890abcdef", 3) == "123##########def"


def test_messages_of() -> None:
    a = TypeError()
    b = ValueError()

    group = ExceptionGroup(str(), (a, b))

    searchers = (
        on("TypeError", [1, 2], else_=[]),
        on("ValueError", [3, 4], else_=[]),
    )

    try:
        errors.messages_of(group, *searchers)
    except ExceptionGroup as error:
        assert group is error

    messages = errors.messages_of(ExceptionGroup(str(), (a, b)), *searchers)
    assert messages == (1, 2, 3, 4)

    searchers = (on("TypeError", [128], else_=[]), to(tuple()))
    messages = errors.messages_of(group, *searchers)
    assert messages == (128, )

    searchers = (on("TypeError", [128], else_=[]), to(tuple()))
    messages = errors.messages_of(group, *searchers)
    assert messages == (128, )


def test_to_decorate() -> None:
    decorator_factory = lib.to_decorate(with_parameters=True)(
        lambda c, a, b: (c() + a) * b
    )

    result = decorator_factory(3, 8)(lambda v: v + 1)(4)
    assert result == 64


    decorator_factory = lib.to_decorate(with_parameters=True)(
        lambda c: str(c())
    )

    result = decorator_factory()(lambda v: v * 2)(128)
    assert result == '256'


    decorator = lib.to_decorate()(lambda c: str(c()))

    result = decorator(lambda v: v * 2)(128)
    assert result == '256'


def test_to_raise_multiple_errors() -> None:
    class A(Exception): ...
    class B(Exception): ...
    class C(Exception): ...

    a = A()
    b = B()
    c = C()

    decorator = validation.to_raise_multiple_errors

    result = decorator(lambda v: [v + 3])(5)
    assert result == 8

    result = decorator(lambda v: [v + 3, ':P'])(5)
    assert result == 8

    result = decorator(lambda v, w: [v + w, a])(3, 5)
    assert result == 8

    result = decorator(to([':P', a, b]))(...)
    assert result == ':P'

    try:
        decorator(to([a]))(...)
    except ExceptionGroup as group:
        assert group.exceptions == (a, )

    try:
        decorator(to([a, ':P', b]))(...)
    except ExceptionGroup as group:
        assert group.exceptions == (a, )

    try:
        decorator(to([a, b, ':P', c]))(...)
    except ExceptionGroup as group:
        assert group.exceptions == (a, b)

    try:
        decorator(to([a, validation.last(b), c, ':P']))(...)
    except ExceptionGroup as group:
        assert group.exceptions == (a, b)

    try:
        decorator(to([a, b]))(...)
    except ExceptionGroup as group:
        assert group.exceptions == (a, b)

    try:
        decorator(to([a, validation.last(b), c]))(...)
    except ExceptionGroup as group:
        assert group.exceptions == (a, b)

    result = decorator(to([]))(...)
    assert result is None

    result = decorator(to([validation.as_result(a), ':P']))(...)
    assert result is a

    result = decorator(to([validation.as_result(a), b]))(...)
    assert result is a

    try:
        decorator(to([a, validation.as_result(b), c, ':P']))(...)
    except ExceptionGroup as group:
        assert group.exceptions == (a, )

    result = decorator(to([raise_]))(...)
    assert result is None

    try:
        decorator(to([raise_, a]))(...)
    except ExceptionGroup as group:
        assert group.exceptions == (a, )

    result = decorator(to([':P', raise_, a]))(...)
    assert result == ':P'

    try:
        decorator(to([a, b, raise_]))(...)
    except ExceptionGroup as group:
        assert group.exceptions == (a, b)

    try:
        decorator(to([a, b, raise_, ':P']))(...)
    except ExceptionGroup as group:
        assert group.exceptions == (a, b)

    try:
        decorator(to([a, b, raise_, c, ':P']))(...)
    except ExceptionGroup as group:
        assert group.exceptions == (a, b, )

    result = decorator(to([raise_, ':P']))(...)
    assert result == ':P'

    try:
        decorator(to([raise_, a, ':P']))(...)
    except ExceptionGroup as group:
        assert group.exceptions == (a, )

    def generate():
        if False:
            yield ...

        return ':P'

    result = decorator(generate)()
    assert result == ':P'

    def generate():
        yield ':P'

    result = decorator(generate)()
    assert result == ':P'

    def generate():
        yield a
        yield 4
        return ':P'


    try:
        decorator(generate)()
    except ExceptionGroup as group:
        assert group.exceptions == (a, )


def test_returning_iterator() -> None:
    assert tuple(lib.ReturningIterator(iter([1, 2, 3]))) == (1, 2, 3)

    def generate():
        yield 1
        return 2

    assert tuple(lib.ReturningIterator(generate())) == (1, 2)

    def generate():
        yield 1

    assert tuple(lib.ReturningIterator(generate())) == (1, )

    def generate():
        yield 1
        return ok(2)

    assert tuple(lib.ReturningIterator(generate())) == (1, 2)

    def generate():
        yield 1
        return ok(None)

    assert tuple(lib.ReturningIterator(generate())) == (1, None)


def test_latest() -> None:
    result = tuple(validation.latest([]))
    assert result == tuple()

    result = tuple(validation.latest([1]))
    assert result == (validation.last(1), )

    result = tuple(validation.latest([1, 2]))
    assert result == (1, validation.last(2))

    result = tuple(validation.latest([1, 2, 3]))
    assert result == (1, 2, validation.last(3))

    result = tuple(validation.latest(range(256)))
    assert result == (*range(255), validation.last(255))


def test_exists() -> None:
    result = validation.exists(None, ':P')
    assert result == (':P', )

    result = tuple(validation.exists(None, None))
    assert result == (None, )

    result = tuple(validation.exists(':P', None))
    assert result == tuple()

    result = tuple(validation.exists(':P', ':D'))
    assert result == tuple()

    result = tuple(validation.exists(':P', 1, 2, 3))
    assert result == tuple()

    result = tuple(validation.exists(None, 1, 2, 3))
    assert result == (1, 2, 3)
