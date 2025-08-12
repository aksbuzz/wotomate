from abc import ABC, abstractmethod
from typing import List, Optional

from project.domain.models.workflow import Workflow

class IWorkflowRepository(ABC):
    @abstractmethod
    def save(self, workflow: Workflow) -> None:
        pass

    @abstractmethod
    def get_by_id(self, id: int) -> Optional[Workflow]:
        pass
        
    @abstractmethod
    def list_by_user(self, user_id: int) -> List[Workflow]:
        pass