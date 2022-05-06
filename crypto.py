# vault.py

import base64

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class Encoder:
    def __init__(self, login, password):
        self.safe_key = self._get_safe_key(login, password)
        self.fernet = Fernet(self.safe_key)

    def _get_safe_key(self, login, password):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'128',
            iterations=4096
        )
        return base64.urlsafe_b64encode(
            kdf.derive(f'{login}-{password}'.encode())
        )

    def encode(self, key):
        return self.fernet.encrypt(key.encode()).decode()

    def decode(self, token):
        return self.fernet.decrypt(token.encode()).decode()
