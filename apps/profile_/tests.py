from apps.profile_ import lib


def test_half_hidden() -> None:
    assert lib.half_hidden("12345", 3) == "#####"
    assert lib.half_hidden("1234567890", 3) == "123####890"
    assert lib.half_hidden("1234567890abcdef", 3) == "123##########def"
