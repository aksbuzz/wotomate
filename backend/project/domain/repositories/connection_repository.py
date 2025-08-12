import uuid
from abc import ABC, abstractmethod
from typing import List, Optional
from project.domain.models.connection import Connection

class IConnectionRepository(ABC):
    @abstractmethod
    def save(self, connection: Connection) -> None:
        pass

    @abstractmethod
    def get_by_id(self, id: uuid.UUID) -> Optional[Connection]:
        """Retrieves a connection by its ID."""
        pass

    @abstractmethod
    def find_by_user(self, user_id: int) -> List[Connection]:
        """Finds all connections for a given user."""
        pass

    @abstractmethod
    def find_by_user_and_connector(self, user_id: int, connector_key: str) -> Optional[Connection]:
        pass