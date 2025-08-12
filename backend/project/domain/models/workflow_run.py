from enum import Enum
from datetime import datetime
from typing import List, Dict, Any, Optional

class RunStatus(str, Enum):
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"

class RunActionLog:
    def __init__(
        self,
        id: int,
        action_id: int,
        position: int,
        status: RunStatus,
        started_at: datetime,
        finished_at: Optional[datetime] = None,
        input_data: Optional[Dict[str, Any]] = None,
        output_data: Optional[Dict[str, Any]] = None,
        log_message: Optional[str] = None
    ):
        self.id = id
        self.action_id = action_id
        self.position = position
        self.status = status
        self.started_at = started_at
        self.finished_at = finished_at
        self.input_data = input_data
        self.output_data = output_data
        self.log_message = log_message


class WorkflowRun:
    def __init__(
        self,
        id: int,
        workflow_id: int,
        status: RunStatus,
        started_at: datetime,
        trigger_event_data: dict,
        action_logs: Optional[List[RunActionLog]] = None,
        finished_at: Optional[datetime] | None = None
    ):
        self.id = id
        self.workflow_id = workflow_id
        self._status = status
        self.started_at = started_at
        self.finished_at = finished_at
        self.trigger_event_data = trigger_event_data
        self._action_logs = action_logs or []

    @property
    def status(self) -> RunStatus: return self._status
    
    @property
    def action_logs(self) -> List[RunActionLog]: return self._action_logs.copy()

    @staticmethod
    def start(workflow_id: int, trigger_event_data: dict) -> "WorkflowRun":
        return WorkflowRun(
            id=None,
            workflow_id=workflow_id,
            status=RunStatus.RUNNING,
            started_at=datetime.utcnow(),
            trigger_event_data=trigger_event_data
        )

    def record_action_success(self, action_id: int, position: int, input_data: dict, output_data: dict):
        if self._status != RunStatus.RUNNING:
            return
            
        log = RunActionLog(
            id=None,
            action_id=action_id,
            position=position,
            status=RunStatus.SUCCEEDED,
            started_at=datetime.utcnow(),
            finished_at=datetime.utcnow(),
            input_data=input_data,
            output_data=output_data
        )
        self._action_logs.append(log)

    def record_action_failure(self, action_id: int, position: int, input_data: dict, error_message: str):
        if self._status != RunStatus.RUNNING:
            return
        
        log = RunActionLog(
            id=None,
            action_id=action_id,
            position=position,
            status=RunStatus.FAILED,
            started_at=datetime.utcnow(),
            finished_at=datetime.utcnow(),
            input_data=input_data,
            log_message=error_message
        )
        self._action_logs.append(log)
        
        # if any action fails, the whole run fails.
        self._fail()

    def complete(self):
        if self._status == RunStatus.RUNNING:
            self._status = RunStatus.SUCCEEDED
            self.finished_at = datetime.utcnow()
    
    def _fail(self):
        self._status = RunStatus.FAILED
        self.finished_at = datetime.utcnow()