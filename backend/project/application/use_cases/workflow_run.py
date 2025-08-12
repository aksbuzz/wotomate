from typing import Any, Dict

from project.domain.models.workflow_run import WorkflowRun
from project.domain.repositories.workflow_run_repository import IWorkflowRunRepository

class WorkflowRunUseCases:
    def __init__(self, workflow_run_repository: IWorkflowRunRepository):
        self.workflow_run_repository = workflow_run_repository

    def get_run_history(self, run_id: int) -> Dict[str, Any]:
        run = self.workflow_run_repository.get_by_id(run_id)
        if not run:
            return None

        return {
            "id": run.id,
            "workflow_id": run.workflow_id,
            "status": run.status.value,
            "started_at": run.started_at.isoformat(),
            "finished_at": run.finished_at.isoformat() if run.finished_at else None,
            "trigger_event_data": run.trigger_event_data,
            "action_logs": [
                {
                    "action_id": log.action_id,
                    "position": log.position,
                    "status": log.status.value,
                    "started_at": log.started_at.isoformat(),
                    "finished_at": log.finished_at.isoformat() if log.finished_at else None,
                    "input_data": log.input_data,
                    "output_data": log.output_data,
                    "log_message": log.log_message
                }
                for log in run.action_logs
            ]
        }