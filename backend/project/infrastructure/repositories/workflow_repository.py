from project.domain.models.workflow import Workflow, Action, Trigger, WorkflowStatus

from project.infrastructure.models.workflow import Workflow as SQLWorkflow
from project.infrastructure.models.action import Action as SQLAction
from project.infrastructure.models.trigger import Trigger as SQLTrigger

class WorkflowMapper:
    @staticmethod
    def to_domain(sql_workflow: SQLWorkflow) -> Workflow:
        domain_trigger = None
        if sql_workflow.trigger:
            domain_trigger = Trigger(
                id=sql_workflow.trigger.id,
                trigger_definition_id=sql_workflow.trigger.trigger_definition_id,
                config=sql_workflow.trigger.config or {}
            )

        domain_actions = [
            Action(
                id=sql_action.id,
                action_definition_id=sql_action.action_definition_id,
                position=sql_action.position,
                config=sql_action.config or {},
            )
            for sql_action in sql_workflow.actions
        ]

        return Workflow(
            id=sql_workflow.id,
            name=sql_workflow.name,
            user_id=sql_workflow.user_id,
            status=sql_workflow.user_id,
            trigger=domain_trigger,
            actions=domain_actions
        )
    
    @staticmethod
    def from_domain(workflow: Workflow, sql_workflow: SQLWorkflow):
        sql_workflow.name = workflow.name
        sql_workflow.status = workflow.status
        sql_workflow.user_id = workflow.user_id

        if workflow.trigger:
            if sql_workflow.trigger:
                sql_workflow.trigger.trigger_definition_id = workflow.trigger.trigger_definition_id
                sql_workflow.trigger.config = workflow.trigger.config
            else:
                sql_workflow.trigger = SQLTrigger(
                    workflow_id=sql_workflow.id,
                    trigger_definition_id=workflow.trigger.trigger_definition_id,
                    config=workflow.trigger.config
                )
        else:
            if sql_workflow.trigger:
                sql_workflow.trigger = None

        # TODO: left