import secrets
import os
from project import db
from urllib.parse import urlencode
from flask import Blueprint, current_app, jsonify, render_template, request, session
from flask_jwt_extended import get_jwt_identity, jwt_required
import requests
from project.models import Connector
from project.utils import encrypt_value

TRELLO_API_KEY = os.getenv('TRELLO_API_KEY')

trello_auth_bp = Blueprint('trello_auth_bp', __name__)

@trello_auth_bp.route('/initiate', methods=['GET'])
@jwt_required()
def trello_connect_initiate():
  auth_params = {
    'key': TRELLO_API_KEY,
    'scope': "read,write",
    'expiration': "never",
    'callback_method': 'postMessage',
    'return_url': 'http://localhost:5000/api/connection/trello/popup_callback'
  }

  authorization_url = f"https://trello.com/1/authorize?{urlencode(auth_params)}"
  return jsonify({ 'authorization_url': authorization_url })


@trello_auth_bp.route('/popup_callback', methods=['GET'])
def trello_popup_callback_receiver():
  return """
  <!DOCTYPE html>
  <html>
  <head><title>Trello Auth</title></head>
  <body>
      <p>Trello authorization in progress...</p>
      <p>You can close this window if it doesn't close automatically.</p>
      <script>
          if (window.opener) {
              // Optionally, send a generic success/close signal if the main page needs it beyond Trello's direct post.
              // window.opener.postMessage({ type: 'trelloPopupClosed' }, '*');
          }
          setTimeout(function() { window.close(); }, 1000); // Attempt to close
      </script>
  </body>
  </html>
  """

@trello_auth_bp.route('/save_token', methods=['POST'])
@jwt_required()
def trello_save_token():
  current_user_id = get_jwt_identity()

  data = request.get_json()
  trello_token = data.get('token')

  if not trello_token:
    return jsonify({ 'err': 'No Trello token provided' }), 400
  
  try:
    user_info_url = f"https://api.trello.com/1/members/me?key={TRELLO_API_KEY}&token={trello_token}"
    user_info_response = requests.get(user_info_url, timeout=10)
    user_info_response.raise_for_status()
    trello_user_data = user_info_response.json()
    trello_username = trello_user_data.get('username', 'User')
    trello_member_id = trello_user_data.get('id')
  except requests.exceptions.RequestException as e:
    current_app.logger.error(f"Failed to fetch Trello user info with new token: {e}")
    return jsonify({"err": "Could not validate Trello token or fetch user info."}), 500
  except Exception as e:
    current_app.logger.error(f"Error processing Trello user info: {e}")
    return jsonify({"err": "Error processing Trello user info."}), 500
  
  trello_service_def_key = "trello"
  encrypted_token = encrypt_value(trello_token)

  connection_details_for_frontend = {
    "service_key": trello_service_def_key,
    "connection_name": f"Trello ({trello_username})",
    "trello_username": trello_username,
    "trello_member_id": trello_member_id,
  }

  existing_connection = Connector.query.filter_by(
    user_id=current_user_id,
    connector_key=trello_service_def_key
  ).first()

  if existing_connection:
    existing_connection.credentials = {
      "api_key": TRELLO_API_KEY,
      "token": encrypted_token,
      "trello_member_id": trello_member_id,
      "trello_username": trello_username
    }

    existing_connection.connection_name = connection_details_for_frontend["connection_name"]
    db.session.add(existing_connection)
    connection_details_for_frontend["id"] = existing_connection.id
    current_app.logger.info(f"Updated Trello connection for user {current_user_id}")
  else:
    new_connection = Connector(
      user_id=current_user_id,
      connector_key=trello_service_def_key,
      connection_name=connection_details_for_frontend["connection_name"],
      credentials={
        "api_key": TRELLO_API_KEY,
        "token": encrypted_token,
        "trello_member_id": trello_member_id,
        "trello_username": trello_username
      }
    )
    db.session.add(new_connection)
    db.session.flush()
    connection_details_for_frontend['id'] = new_connection.id
    current_app.logger.info(f"Created new Trello connection for user {current_user_id}")

  try:
    db.session.commit()
  except Exception as e:
    db.session.rollback()
    current_app.logger.error(f"Database error storing Trello connection: {e}")
    return jsonify({"err": "Could not save connection."}), 500
  
  return jsonify({ "msg": "Trello token saved successfully", "connectionDetails": connection_details_for_frontend }), 200

