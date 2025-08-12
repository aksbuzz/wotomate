from enum import Enum
from typing import Optional, List

from project.domain.exceptions.domain_exception import DomainException

class WorkflowStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"

class Trigger:
    def __init__(
        self,
        id: int,
        trigger_definition_id: int,
        config: dict
    ):
        self.id = id
        self.trigger_definition_id = trigger_definition_id
        self.config = config

class Action:
    def __init__(
        self,
        id: int,
        action_definition_id: int,
        position: int,
        config: dict
    ):
        self.id = id
        self.action_definition_id = action_definition_id
        self.position = position
        self.config = config


class Workflow:
    def __init__(
        self,
        id: int,
        name: str,
        user_id: int,
        status: WorkflowStatus,
        trigger: Optional[Trigger] = None,
        actions: Optional[List[Action]] = None
    ):
        self.id = id
        self._name = name
        self._user_id = user_id
        self._status = status
        self._trigger = trigger
        self._actions = sorted(actions, key=lambda a: a.position) if actions else []

    @property
    def name(self) -> str: return self._name
    
    @property
    def user_id(self) -> int: return self._user_id
    
    @property
    def status(self) -> WorkflowStatus: return self._status
    
    @property
    def trigger(self) -> Optional[Trigger]: return self._trigger
    
    @property
    def actions(self) -> List[Action]: return self._actions.copy()

    @staticmethod
    def create(name: str, user_id: int) -> "Workflow":
        return Workflow(id=None, name=name, user_id=user_id, status=WorkflowStatus.DRAFT)

    def publish(self):
        if self._status == WorkflowStatus.PUBLISHED:
            return

        if not self._trigger:
            raise DomainException("Cannot publish a workflow without a trigger.")
        
        if not self._actions:
            raise DomainException("Cannot publish a workflow without at least one action.")
        
        self._status = WorkflowStatus.PUBLISHED

    def unpublish(self):
        if self._status == WorkflowStatus.DRAFT:
            return

        self._status = WorkflowStatus.DRAFT
    
    def revert_to_draft(self):
        self._status = WorkflowStatus.DRAFT

    def update_name(self, new_name: str):
        if not new_name:
            raise DomainException("Workflow name cannot be empty.")
        self._name = new_name
    
    def set_trigger(self, trigger: Trigger):
        self._trigger = trigger
    
    def add_action(self, action: Action):
        if any(a.position == action.position for a in self._actions):
            raise DomainException(f"An action with position {action.position} already exists.")
        
        self._actions.append(action)
        self._actions.sort(key=lambda a: a.position)