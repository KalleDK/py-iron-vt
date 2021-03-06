import pathlib

from typing import Union

from .vault import BaseVault, PathLike, Safe, IronVaultError
from .backend.json_backend import JSONBackend
from .encryptor import FernetEncryptor


VERSION = "0.1.1"


class Vault(BaseVault):
    def __init__(self, path: Union[str, PathLike] = "./vt", b64_encode: bool = True):
        backend = JSONBackend(path=pathlib.Path(path), b64_encode=b64_encode)
        encryptor_cls = FernetEncryptor
        super().__init__(backend, encryptor_cls)


def load(name: str, key: str, path: Union[str, PathLike] = "./vt"):
    return Vault(path).load(name, key)


__all__ = ["Vault", "Safe", "IronVaultError", "VERSION"]
