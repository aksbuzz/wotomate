from flask import Blueprint, request, jsonify, current_app
from project import db
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from project.models import ConnectorDefinition, TriggerDefinition, ActionDefinition, Connector
from sqlalchemy.orm import joinedload
from project.utils import serialize_definitions, serialize_trigger_action_definitions
 
connector_bp = Blueprint('connector_bp', __name__)

@connector_bp.route('/definitions', methods=['GET'])
def get_all_connectors_definitions():
  try:
    connector_defs = ConnectorDefinition.query.order_by(ConnectorDefinition.display_name).all()
    if not connector_defs:
      return jsonify({"msg": "No connector definitions found."}), 404
    
    return jsonify({ "data": serialize_definitions(connector_defs) }), 200 
  
  except Exception as e:
        current_app.logger.error(f"An error occured: {e}")
        return jsonify({"err": "An internal error occurred"}), 500


@connector_bp.route('/definitions/<string:connector_key>/triggers', methods=['GET'])
def get_trigger_definitions_for_connector(connector_key):
  connector_def = ConnectorDefinition.query.filter_by(key=connector_key).first()
  if not connector_def:
    return jsonify({ "err": f"Connector with key '{connector_key}' not found."}), 404
  
  triggers = TriggerDefinition.query.filter_by(
     connector_definition_id=connector_def.id
  ).options(joinedload(TriggerDefinition.connector_definition)).all()

  return jsonify(serialize_trigger_action_definitions(triggers)), 200

@connector_bp.route('/definitions/<string:connector_key>/actions', methods=['GET'])
def get_action_definitions_for_connector(connector_key):
  connector_def = ConnectorDefinition.query.filter_by(key=connector_key).first()
  if not connector_def:
    return jsonify({ "err": f"Connector with key '{connector_key}' not found."}), 404
  
  actions = ActionDefinition.query.filter_by(
     connector_definition_id=connector_def.id
  ).options(joinedload(ActionDefinition.connector_definition)).all()

  return jsonify(serialize_trigger_action_definitions(actions)), 200


@connector_bp.route('/', methods=['GET'])
@jwt_required()
def get_connectors_for_user():
  current_user_id = get_jwt_identity()
  connections = Connector.query.filter_by(
    user_id=current_user_id
  ).all()

  result = []
  for conn in connections:
    result.append({
      "id": conn.id,
      "connector_key": conn.connector_key,
      "connection_name": conn.connection_name,
      "created_at": conn.created_at,
      "updated_at": conn.updated_at,
    })

  return jsonify(result),  200


@connector_bp.route('/status/<string:connector_key>', methods=['GET'])
@jwt_required()
def check_connection_status(connector_key):
  current_user_id = get_jwt_identity()
  connection = Connector.query.filter_by(
    user_id=current_user_id,
    connector_key=connector_key
  ).first()

  if connection:
    return jsonify({
      "connected": True,
      "id": connection.id,
      "connection_name": connection.connection_name,
      "connector_key": connection.connector_key
    }), 200
  else:
    return jsonify({ "connected": False, "connector_key": connector_key }), 200
  
