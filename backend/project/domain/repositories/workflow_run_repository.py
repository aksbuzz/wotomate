from abc import ABC, abstractmethod
from project.domain.models.workflow_run import WorkflowRun

class IWorkflowRunRepository(ABC):
    @abstractmethod
    def save(self, run: WorkflowRun) -> None:
        pass

    @abstractmethod
    def get_by_id(self, id: int) -> WorkflowRun | None:
        pass