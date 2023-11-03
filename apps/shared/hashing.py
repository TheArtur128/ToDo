from act import obj
from cryptography.fernet import Fernet

from apps.shared.types_ import Hash


__all__ = ("hashed", "unhashed")


@obj
class _cryptography_hashing:
    _fernet = Fernet(Fernet.generate_key())

    def hashed(self, line: str) -> Hash:
        return self._fernet.encrypt(line.encode()).decode()

    def unhashed(self, hash: Hash) -> str:
        return self._fernet.decrypt(hash.encode()).decode()


hashed = _cryptography_hashing.hashed
unhashed = _cryptography_hashing.unhashed
