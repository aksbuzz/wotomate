import uuid
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
from typing import Optional

class ConnectionStatus(str, Enum):
    ACTIVE = "active"
    REVOKED = "revoked"
    ERROR = "error"

@dataclass(frozen=True)
class EncryptedCredentials:
    """encrypted credential data"""
    value: bytes


class Connection:
    def __init__(
        self,
        id: int,
        user_id: int,
        connector_key: str,
        connection_name: str,
        credentials: EncryptedCredentials,
        status: ConnectionStatus,
        created_at: datetime,
        updated_at: datetime
    ):
        self.id = id
        self._user_id = user_id
        self._connector_key = connector_key
        self._connection_name = connection_name
        self._credentials = credentials
        self._status = status
        self._created_at = created_at
        self._updated_at = updated_at
    
    @property
    def user_id(self) -> int:
        return self._user_id

    @property
    def connector_key(self) -> int:
        return self._connector_key
        
    @property
    def connection_name(self) -> Optional[str]:
        return self._connection_name

    @property
    def credentials(self) -> EncryptedCredentials:
        return self._credentials

    @property
    def status(self) -> ConnectionStatus:
        return self._status

    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @property
    def updated_at(self) -> datetime:
        return self._updated_at
    
    @staticmethod
    def create(
        user_id: int,
        connector_key: str,
        credentials: EncryptedCredentials,
        connection_name: Optional[str] = None,
    ) -> "Connection":
        if user_id <= 0:
            raise ValueError("User ID must be positive")
        if not connector_key or not connector_key.strip():
            raise ValueError("Connector key cannot be empty")

        now = datetime.now(datetime.timezone.utc)
        return Connection(
            id=0,
            user_id=user_id,
            connector_key=connector_key,
            connection_name=connection_name,
            credentials=credentials,
            status=ConnectionStatus.ACTIVE,
            created_at=now,
            updated_at=now
        )
    
    def update_credentials(self, new_credentials: EncryptedCredentials):
        if not new_credentials:
            raise ValueError("New credentials cannot be empty")
        
        self._credentials = new_credentials
        self._updated_at = datetime.now(datetime.timezone.utc)
        
        if self._status == ConnectionStatus.ERROR:
            self._status = ConnectionStatus.ACTIVE

    def revoke(self):
        if self._status == ConnectionStatus.REVOKED:
            return

        self._status = ConnectionStatus.REVOKED
        self._updated_at = datetime.utcnow()

    def mark_as_error(self):
        if self._status == ConnectionStatus.ERROR:
            return
            
        self._status = ConnectionStatus.ERROR
        self._updated_at = datetime.utcnow()

    def is_usable(self) -> bool:
        return self._status == ConnectionStatus.ACTIVE