from pytest import mark

from apps.shared import hashing


@mark.parametrize("text", ["some mega secrect", str()])
def test_hashing_isomorphism(text: str) -> None:
    assert hashing.unhashed(hashing.hashed(text)) == text
