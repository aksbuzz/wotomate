from flask import Blueprint, request, jsonify
from project import db
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from project.models import Workflow, User, Trigger, Action, TriggerDefinition
from sqlalchemy.orm import joinedload

workflow_bp = Blueprint('workflow_bp', __name__)

@workflow_bp.route('/', methods=['POST'])
@jwt_required()
def create_new_workflow():
  data = request.get_json()
  
  current_user_id = get_jwt_identity()
  user = User.query.filter_by(id=current_user_id).first_or_404()

  if not data or 'name' not in data:
    return jsonify({"err": "Missing required fields: name "}), 400
  
  new_workflow = Workflow(
    name=data['name'],
    user_id = current_user_id,
    owner = user,
    is_active = True,
    status = 'draft',
  )

  db.session.add(new_workflow)
  db.session.commit()

  return jsonify({ "workflow_id": new_workflow.id }), 201


@workflow_bp.route('/<int:workflow_id>', methods=['PUT'])
@jwt_required()
def update_workflow(workflow_id):
  data = request.get_json()
  current_user_id = get_jwt_identity()
  workflow = Workflow.query.filter_by(id=workflow_id, user_id=current_user_id).first_or_404()

  if not data or 'name' not in data:
    return jsonify({"err": "Missing required fields: name "}), 400
  
  workflow.name = data['name']
  workflow.is_active = data.get('is_active', workflow.is_active)
  workflow.status = data.get('status', workflow.status)

  db.session.commit()

  return jsonify({ "workflow_id": workflow.id }), 200

@workflow_bp.route('/', methods=['GET'])
@jwt_required()
def get_workflows():
  current_user_id = get_jwt_identity()
  user = User.query.filter_by(id=current_user_id).first_or_404()
  
  workflows = [
    {
      "id": w.id, 
      "name": w.name, 
      "is_active": w.is_active,
      "status": w.status, 
      "created_at": w.created_at.isoformat(), 
      "updated_at": w.updated_at.isoformat()
    }
      for w in user.workflows
    ]
  
  return jsonify(workflows), 200


@workflow_bp.route('/<int:workflow_id>', methods=['GET'])
@jwt_required()
def get_workflow(workflow_id):
  current_user_id = get_jwt_identity()
  workflow = Workflow.query.filter_by(id=workflow_id, user_id=current_user_id).first_or_404()
  
  trigger = None
  if workflow.trigger:
      trigger = {
          "id": workflow.trigger.id,
          "workflow_id": workflow.trigger.workflow_id,
          "trigger_definition_id": workflow.trigger.trigger_definition_id,
          "config": workflow.trigger.config,
          "connector_id": workflow.trigger.connector_id,
          "webhook_id": workflow.trigger.webhook_id,
          "created_at": workflow.trigger.created_at.isoformat() if workflow.trigger.created_at else None,
          "updated_at": workflow.trigger.updated_at.isoformat() if workflow.trigger.updated_at else None,
      }

  actions_query = workflow.actions
  if hasattr(actions_query, 'all'):
      actions_list = actions_query.all()
  else:
      actions_list = actions_query

  # Serialize actions
  actions = []
  for action in actions_list:
      actions.append({
          "id": action.id,
          "workflow_id":action.workflow_id,
          "action_definition_id": action.action_definition_id,
          "config": action.config,
          "position": action.position,
          "connector_id": action.connector_id,
          "created_at": action.created_at.isoformat() if action.created_at else None,
          "updated_at": action.updated_at.isoformat() if action.updated_at else None,
      })

  workflow_data = {
      "id": workflow.id,
      "name": workflow.name,
      "is_active": workflow.is_active,
      "status": workflow.status,
      "created_at": workflow.created_at.isoformat() if workflow.created_at else None,
      "updated_at": workflow.updated_at.isoformat() if workflow.updated_at else None,
      "trigger": trigger,
      "actions": actions,
  }
  return jsonify(workflow_data), 200

@workflow_bp.route('/<int:workflow_id>/trigger', methods=['POST', 'PUT'])
@jwt_required()
def upsert_trigger(workflow_id):
    current_user_id = get_jwt_identity()
    workflow = Workflow.query.filter_by(id=workflow_id, user_id=current_user_id).first_or_404()
    data = request.get_json()

    if not data or 'trigger_definition_id' not in data:
        return jsonify({"err": "Missing required field: trigger_definition_id"}), 400
  
    trigger_def = TriggerDefinition.query.get(data['trigger_definition_id'])

    # If trigger exists, update it; else, create new
    if workflow.trigger:
        workflow.trigger.trigger_definition_id = data['trigger_definition_id']
        workflow.trigger.trigger_definition = trigger_def
        workflow.trigger.config = data.get('config', workflow.trigger.config)
        workflow.trigger.connector_id = data.get('connector_id', workflow.trigger.connector_id)
        workflow.trigger.webhook_id = data.get('webhook_id', workflow.trigger.webhook_id)
    else:
        trigger = Trigger(
            workflow_id=workflow.id,
            trigger_definition_id=data['trigger_definition_id'],
            trigger_definition=trigger_def,
            config=data.get('config', {}),
            connector_id=data.get('connector_id'),
            webhook_id=data.get('webhook_id', None)
        )
        db.session.add(trigger)

    db.session.commit()
    return jsonify({"msg": "Trigger upserted"}), 201


@workflow_bp.route('/<int:workflow_id>/actions', methods=['POST', 'PUT'])
@jwt_required()
def upsert_actions(workflow_id):
    current_user_id = get_jwt_identity()
    workflow = Workflow.query.filter_by(id=workflow_id, user_id=current_user_id).first_or_404()
    data = request.get_json()

    if not data or 'actions' not in data or not isinstance(data['actions'], list):
        return jsonify({"err": "Missing or invalid 'actions' list"}), 400

    # Remove actions not present in the update (if PUT)
    if request.method == 'PUT':
        incoming_ids = [a.get('id') for a in data['actions'] if a.get('id')]
        for action in workflow.actions:
            if action.id not in incoming_ids:
                db.session.delete(action)

    # Update or add actions
    for action_data in data['actions']:
        if 'id' in action_data:
            action = workflow.actions.filter_by(id=action_data['id']).first()
            if action:
                action.action_definition_id = action_data.get('action_definition_id', action.action_definition_id)
                action.config = action_data.get('config', action.config)
                action.position = action_data.get('position', action.position)
                action.connector_id = action_data.get('connector_id', action.connector_id)
        else:
            action = Action(
                workflow_id=workflow.id,
                action_definition_id=action_data['action_definition_id'],
                config=action_data.get('config', {}),
                position=action_data.get('position', 0),
                connector_id=action_data.get('connector_id'),
            )
            db.session.add(action)

    db.session.commit()
    return jsonify({"msg": "Actions upserted"}), 200