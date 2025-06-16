# from datetime import datetime
# from flask import current_app
# import traceback

# from .. import db
# from ..models import WorkflowRun, Workflow, User, ConnectedService
# from ..enums import ActionType, TriggerType, WorkflowStatus
# from .actions_handler import ACTION_HANDLERS

def execute_workflow(workflow_id: int, trigger_data: dict = None):
    # current_app.logger.info(f"Attempting to execute workflow {workflow_id}")
    # workflow = Workflow.query.get(workflow_id)

    # if not workflow:
    #     current_app.logger.error(f"Workflow {workflow_id} not found")
    #     return None
    
    # if not workflow.is_active:
    #     current_app.logger.warning(f"Workflow {workflow_id} is not active")
    #     return None
    
    # run = WorkflowRun(
    #     workflow_id=workflow.id,
    #     status=WorkflowStatus.RUNNING,
    #     trigger_data=trigger_data or {},
    # )
    # db.session.add(run)
    # db.session.commit()

    # current_app.logger.info(f"Created workflow run {run.id} for workflow {workflow_id}")

    # try:
    #     context_data = {
    #         "worflow": {
    #             "id": workflow.id,
    #             "name": workflow.name,
    #             "user_id": workflow.user_id
    #         },
    #         "trigger_data": run.trigger_data,
    #         "run": {
    #             "id": run.id,
    #             "started_at": run.started_at.isoformat(),
    #         }
    #     }
        
    #     action_handler = ACTION_HANDLERS.get(workflow.action_type)
    #     if not action_handler:
    #         run.status = WorkflowStatus.FAILED
    #         run.log_message = f"Unsupported action type: {workflow.action_type}"
    #         current_app.logger.error(run.log_message)
    #     else:
    #         current_app.logger.info(f"Executing action handler for workflow {workflow_id}")
    #         success = action_handler(workflow.action_config, context_data, run)
    #         run.status = WorkflowStatus.SUCCESS if success else WorkflowStatus.FAILED
    
    # except Exception as e:
    #     current_app.logger.exception(f"Unhandled exception during workflow {workflow_id} run {run.id} execution")
    #     run.status = WorkflowStatus.FAILED
    #     run.log_message = f"Error executing workflow: {str(e)}\n{traceback.format_exc()}"
    #     if not run.action_data:
    #         run.action_data = {"error": str(e)}
    # finally:
    #     run.finished_at = datetime.utcnow()
    #     workflow.last_run_at = run.finished_at
    #     db.session.commit()
    #     current_app.logger.info(f"Workflow run {run.id} completed with status {run.status}")
    
    # return {
    #     "id": run.id,
    #     "workflow_id": workflow.id,
    #     "status": run.status.value if hasattr(run.status, 'value') else run.status,
    #     "log_message": run.log_message,
    #     "started_at": run.started_at.isoformat(),
    #     "finished_at": run.finished_at.isoformat() if run.finished_at else None,
    # }
    pass
