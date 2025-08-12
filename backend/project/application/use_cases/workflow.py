from typing import Any, List, Dict

from project.domain.models.workflow import Workflow, Trigger, Action
from project.domain.repositories.workflow_repository import IWorkflowRepository
from project.application.services import IUnitOfWork

class WorkflowUseCases:
    def __init__(self, workflow_repository: IWorkflowRepository, uow: IUnitOfWork):
        self.workflow_repository = workflow_repository
        self.uow = uow

    def create_workflow(self, user_id: int, name: str) -> Workflow:
        with self.uow:
            new_workflow = Workflow.create(name=name, user_id=user_id)
            self.workflow_repository.save(new_workflow)
            self.uow.commit()

            return new_workflow
        
    def update_workflow(self, workflow_id: int, user_id: int, name: str, trigger_data: Dict[str, Any], actions_data: List[Dict[str, Any]]) -> Workflow:
        with self.uow:
            workflow = self.workflow_repository.get_by_id(workflow_id)
            if not workflow:
                raise ValueError("Workflow not found")
            if workflow.user_id != user_id:
                raise PermissionError("User is not authorized to edit this workflow.")
            
            workflow.update_name(name)

            new_trigger = Trigger(
                id=trigger_data.get('id'),
                trigger_definition_id=trigger_data['trigger_definition_id'],
                config=trigger_data['config']
            )
            workflow.set_trigger(new_trigger)

            workflow._actions.clear()
            for action_data in actions_data:
                new_action = Action(
                    id=action_data.get('id'),
                    action_definition_id=action_data['action_definition_id'],
                    position=action_data['position'],
                    config=action_data['config']
                )
                workflow.add_action(new_action)

            self.workflow_repository.save(workflow)
            self.uow.commit()

            return workflow
        
    def publish_workflow(self, workflow_id: int, user_id: int) -> Workflow:
        with self.uow:
            workflow = self.workflow_repository.get_by_id(workflow_id)
            if not workflow:
                raise ValueError("Workflow not found")
            if workflow.user_id != user_id:
                raise PermissionError("User is not authorized to publish this workflow.")
            
            workflow.publish()

            self.workflow_repository.save(workflow)
            self.uow.commit()

            return workflow

    def unpublish_workflow(self, workflow_id: int, user_id: int) -> Workflow:
        with self.uow:
            workflow = self.workflow_repository.get_by_id(workflow_id)
            if not workflow:
                raise ValueError("Workflow not found")
            if workflow.user_id != user_id:
                raise PermissionError("User is not authorized to publish this workflow.")
            
            workflow.unpublish()

            self.workflow_repository.save(workflow)
            self.uow.commit()

            return workflow
        
    def get_workflow_details(self, workflow_id: int, user_id: int) -> Dict[str, Any]:
        workflow = self.workflow_repository.get_by_id(workflow_id)
        if not workflow or workflow.user_id != user_id:
            return None

        return self._format_workflow_dto(workflow)

    def list_workflows_for_user(self, user_id: int) -> List[Dict[str, Any]]:
        workflows = self.workflow_repository.list_by_user(user_id)
        return [self._format_workflow_dto(w) for w in workflows]
    
    def _format_workflow_dto(self, workflow: Workflow) -> Dict[str, Any]:
        return {
            "id": workflow.id,
            "name": workflow.name,
            "status": workflow.status.value,
            "trigger": {
                "id": workflow.trigger.id,
                "trigger_definition_id": workflow.trigger.trigger_definition_id,
                "config": workflow.trigger.config
            } if workflow.trigger else None,
            "actions": [
                {
                    "id": action.id,
                    "action_definition_id": action.action_definition_id,
                    "position": action.position,
                    "config": action.config
                }
                for action in workflow.actions
            ]
        }