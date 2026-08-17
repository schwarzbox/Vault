# vault.py

import base64
import unicodedata

from argon2.low_level import Type, hash_secret_raw

from cryptography.fernet import Fernet


class Encoder:
    def __init__(self, login, password):
        self.fernet = Fernet(self._get_safe_key(login, password))

    @staticmethod
    def _get_safe_key(login: str, password: str):
        # Normalize login so equivalent Unicode representations
        login = unicodedata.normalize('NFC', login)
        # Deterministic salt derived from the login.
        salt = login.encode('utf-8')

        key = hash_secret_raw(
            secret=password.encode('utf-8'),
            salt=salt,
            time_cost=3,
            memory_cost=16384,
            parallelism=4,
            hash_len=32,
            type=Type.ID,
        )
        # Fernet requires a URL-safe base64-encoded 32-byte key.
        return base64.urlsafe_b64encode(key)

    def encode(self, key):
        return self.fernet.encrypt(key.encode()).decode()

    def decode(self, token):
        return self.fernet.decrypt(token.encode()).decode()
