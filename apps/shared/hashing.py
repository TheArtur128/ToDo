from act import obj
from cryptography.fernet import Fernet

from apps.shared.types_ import Hash


__all__ = ("hashed", "unhashed")


@obj.of
class _cryptography_hashing:
    __fernet = Fernet(Fernet.generate_key())

    def hashed(line: str) -> Hash:
        return _cryptography_hashing.__fernet.encrypt(line.encode()).decode()

    def unhashed(hash: Hash) -> str:
        return _cryptography_hashing.__fernet.decrypt(hash.encode()).decode()


hashed = _cryptography_hashing.hashed
unhashed = _cryptography_hashing.unhashed
