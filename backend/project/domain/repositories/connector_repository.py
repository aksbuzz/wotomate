from abc import ABC, abstractmethod
from typing import List, Optional
from project.domain.models.connector import Connector

class IConnectorRepository(ABC):
    @abstractmethod
    def get_by_key(self, key: str) -> Optional[Connector]:
        pass
        
    @abstractmethod
    def list_all(self) -> List[Connector]:
        pass