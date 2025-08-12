import os
import json
from cryptography.fernet import Fernet

from project.application.services import IEncryptionService
from project.domain.models.connection import EncryptedCredentials


ENCRYPTION_KEY = os.environ.get('FERNET_ENCRYPTION_KEY').encode()

class CryptographyEncryptionService(IEncryptionService):
    def __init__(self, key: bytes = ENCRYPTION_KEY):
        self._fernet = Fernet(key)

    def encrypt(self, data: dict) -> EncryptedCredentials:
        json_string = json.dumps(data)
        encrypted_bytes = self._fernet.encrypt(json_string.encode('utf-8'))
        return EncryptedCredentials(value=encrypted_bytes)

    def decrypt(self, encrypted_creds: EncryptedCredentials) -> dict:
        decrypted_bytes = self._fernet.decrypt(encrypted_creds.value)
        return json.loads(decrypted_bytes.decode('utf-8'))