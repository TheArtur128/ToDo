from pytest import mark

from apps.shared import hashing, tools


@mark.parametrize("text", ["some mega secrect", str()])
def test_hashing_isomorphism(text: str) -> None:
    assert hashing.unhashed(hashing.hashed(text)) == text


@mark.parametrize("token_length", [*range(10), 32, 64, 128, 1024, 2069])
def test_token_generator_with(token_length: int) -> None:
    generate = tools.token_generator_with(length=token_length)

    assert len(generate()) == token_length
    assert len(generate()) == token_length
    assert len(generate()) == token_length
