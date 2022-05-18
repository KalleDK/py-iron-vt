import os
import base64
import dataclasses


from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from .vault import Entry


def _make_fernet(key: bytes, salt: bytes):
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=390000)
    fern_key = base64.urlsafe_b64encode(kdf.derive(key))
    return Fernet(fern_key)


@dataclasses.dataclass
class FernetEncryptor:
    key: bytes

    def decrypt(self, entry: Entry):
        fernet = _make_fernet(self.key, entry.salt)
        return fernet.decrypt(entry.token)

    def encrypt(self, secret: bytes):
        salt = os.urandom(16)
        fernet = _make_fernet(self.key, salt)
        token = fernet.encrypt(secret)
        return Entry(salt=salt, token=token)
