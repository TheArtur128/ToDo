from pytest import mark

from apps.shared import hashing, lib


@mark.parametrize("text", ["some mega secrect", str()])
def test_hashing_isomorphism(text: str) -> None:
    assert hashing.unhashed(hashing.hashed(text)) == text


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
