from pytest import mark

from apps.confirmation import lib


@mark.parametrize("token_length", [*range(10), 32, 64, 128, 1024, 2069])
def test_token_generator_with(token_length: int) -> None:
    generate = lib.token_generator_with(length=token_length)

    assert len(generate()) == token_length
    assert len(generate()) == token_length
    assert len(generate()) == token_length
