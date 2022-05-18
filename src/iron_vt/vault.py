import sys
import os
import dataclasses

from typing import (
    Mapping,
    MutableMapping,
    Protocol,
    Type,
    Optional,
)


if sys.version_info >= (3, 8):  # coverage: ignore
    PathLike = os.PathLike[str]
else:  # coverage: ignore
    PathLike = os.PathLike


class IronValutError(RuntimeError):
    pass


@dataclasses.dataclass
class Entry:
    salt: bytes
    token: bytes


@dataclasses.dataclass
class Safe:
    name: str
    entries: MutableMapping[str, bytes] = dataclasses.field(default_factory=dict)

    def add(self, name: str, secret: str):
        self.entries[name] = secret.encode("utf-8")

    def get(self, name: str, default: Optional[str] = None):
        value = self.entries.get(name)
        if value is None:
            return default
        return value.decode("utf-8")

    def __getitem__(self, name: str) -> str:
        return self.entries[name].decode("utf-8")

    def __setitem__(self, name: str, value: str) -> None:
        self.entries[name] = value.encode("utf-8")


class Encryptor(Protocol):
    def __init__(self, key: bytes) -> None:
        ...

    def decrypt(self, entry: Entry) -> bytes:
        ...

    def encrypt(self, secret: bytes) -> Entry:
        ...


class Backend(Protocol):
    def load(self, name: str) -> Mapping[str, Entry]:
        ...

    def save(self, name: str, entries: Mapping[str, Entry]) -> None:
        ...

    def exists(self, name: str) -> bool:
        ...


@dataclasses.dataclass
class BaseVault:
    _backend: Backend
    _encryptor_cls: Type[Encryptor]

    def exists(self, name: str):
        return self._backend.exists(name)

    def create(self, name: str):
        return Safe(name)

    def load(self, name: str, key: str) -> Safe:

        encrypted_entries = self._backend.load(name)

        encryptor = self._encryptor_cls(key.encode("utf-8"))

        entries = {
            name: encryptor.decrypt(entry) for name, entry in encrypted_entries.items()
        }

        return Safe(name=name, entries=entries)

    def save(self, safe: Safe, key: str):

        encryptor = self._encryptor_cls(key.encode("utf-8"))

        encrypted_entries = {
            name: encryptor.encrypt(entry) for name, entry in safe.entries.items()
        }

        self._backend.save(safe.name, encrypted_entries)
