from typing import Generic

from act import K, V
from django.core.cache import caches


__all__ = ("CacheRepository", )


class CacheRepository(Generic[K, V]):
    def __init__(self, subject: str, *, salt: str, location: str) -> None:
        self.__subject = subject
        self.__salt = salt
        self.__location = location

    def __repr__(self) -> str:
        return "{}[{}]({}:{})".format(
            type(self).__name__, self.__location, self.__salt, self.__subject
        )

    def __getitem__(self, key: K) -> Optional[V]:
        return caches[self.__location].get(self.__key_for(key))

    def __setitem__(self, key: K, value: V) -> None:
        caches[self.__location].set(self.__key_for(key), value)

    def __delitem__(self, key: K) -> bool:
        return caches[self.__location].delete(key)

    def __key_for(self, *, key: K) -> str:
        return f"{self.__salt}:{self.__subject}:{key}"
