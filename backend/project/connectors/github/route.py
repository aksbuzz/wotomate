import secrets
import os
from project import db
from urllib.parse import urlencode
from flask import Blueprint, current_app, jsonify, render_template, request, session
from flask_jwt_extended import get_jwt_identity, jwt_required
import requests
from project.models import Connector
from project.utils import encrypt_value

GITHUB_CLIENT_ID = os.getenv('GITHUB_CLIENT_ID')
GITHUB_CLIENT_SECRET = os.getenv('GITHUB_CLIENT_SECRET')
GITHUB_REDIRECT_URI = os.getenv('GITHUB_REDIRECT_URI', 'http://localhost:5000/api/connection/github/callback')


github_auth_bp = Blueprint('github_auth_bp', __name__)

@github_auth_bp.route('/initiate', methods=['GET'])
@jwt_required()
def github_connect_initiate():
  state = secrets.token_urlsafe(16)
  session['oauth_state_github'] = state

  scopes = ['repo', 'read:user', 'user:email']

  params = {
    'client_id': GITHUB_CLIENT_ID,
    'redirect_uri': GITHUB_REDIRECT_URI,
    'scope': ' '.join(scopes),
    'state': state,
    'response_type': 'code'
  }

  auth_url = f"https://github.com/login/oauth/authorize?{urlencode(params)}"
  return jsonify({ 'authorization_url': auth_url })


@github_auth_bp.route('/callback', methods=['GET'])
@jwt_required()
def github_connect_callback():
  current_user_id = get_jwt_identity()

  received_code = request.args.get('code')
  received_state = request.args.get('state')
  expected_state = session.pop('oauth_state_github', None)

  if not received_state or received_state != expected_state:
    current_app.logger.error(f"OAuth State mismatch. Expected: {expected_state}, Received: {received_state}")
    return jsonify({"err": "Invalid OAuth state. Possible CSRF attack."}), 400

  if not received_code:
    error = request.args.get('error')
    error_description = request.args.get('error_description')
    current_app.logger.error(f"GitHub OAuth error: {error} - {error_description}")
    return jsonify({"err": f"GitHub OAuth failed: {error_description or error}"}), 400
  
  token_payload = {
    'client_id': GITHUB_CLIENT_ID,
    'client_secret': GITHUB_CLIENT_SECRET,
    'code': received_code,
    'redirect_uri': GITHUB_REDIRECT_URI # Must match the one used in the auth request
  }
  headers = {'Accept': 'application/json'}

  try:
    token_response = requests.post(
        'https://github.com/login/oauth/access_token',
        data=token_payload,
        headers=headers,
        timeout=10
    )
    token_response.raise_for_status()  # Raises HTTPError for bad responses (4XX or 5XX)
    token_data = token_response.json()
  except requests.exceptions.RequestException as e:
    current_app.logger.error(f"Failed to exchange GitHub code for token: {e}")
    return jsonify({"err": "Could not retrieve access token from GitHub."}), 500

  access_token = token_data.get('access_token')
  if not access_token:
      current_app.logger.error(f"No access_token in GitHub response: {token_data}")
      return jsonify({"err": "Access token not found in GitHub response."}), 500
  
  try:
    user_info_headers = {
        'Authorization': f"token {access_token}",
        'Accept': 'application/vnd.github.v3+json'
    }
    user_info_response = requests.get('https://api.github.com/user', headers=user_info_headers, timeout=10)
    user_info_response.raise_for_status()
    github_user_data = user_info_response.json()
  except requests.exceptions.RequestException as e:
    current_app.logger.error(f"Failed to fetch GitHub user info: {e}")
    # Proceed without user_info or handle as critical error
    github_user_data = {}

  github_connector_key = "github"
  encrypted_token = encrypt_value(access_token)

  existing_connection = Connector.query.filter_by(
    user_id=current_user_id,
    connector_key=github_connector_key
  ).first()

  connection_details_for_frontend = {
    "connector_key": github_connector_key,
    "connection_name": f"GitHub ({github_user_data.get('login', 'User')})",
    "github_login": github_user_data.get('login')
  }

  if existing_connection:
    existing_connection.credentials = {
      "access_token": encrypted_token,
      "scopes": token_data.get('scope', '').split(','),
      "token_type": token_data.get('token_type'),
      "github_user_id": github_user_data.get('id'),
      "github_login": github_user_data.get('login')
    }
    existing_connection.connection_name = connection_details_for_frontend["connection_name"]
    db.session.add(existing_connection)
    connection_details_for_frontend["id"] = existing_connection.id
    current_app.logger.info(f"Updated GitHub connection for user {current_user_id}")
  else:
    new_connection = Connector(
      user_id=current_user_id,
      connector_key=github_connector_key,
      connection_name=connection_details_for_frontend["connection_name"],
      credentials={
        "access_token": encrypted_token,
        "scopes": token_data.get('scope', '').split(','),
        "token_type": token_data.get('token_type'),
        "github_user_id": github_user_data.get('id'),
        "github_login": github_user_data.get('login')
      }
    )
    db.session.add(new_connection)
    db.session.flush()
    connection_details_for_frontend['id'] = new_connection.id
    current_app.logger.info(f"Created GitHub connection for user {current_user_id}")

  try:
    db.session.commit()
  except Exception as e:
    db.session.rollback()
    current_app.logger.error(f"Database error storing GitHub connection: {e}")
    return jsonify({"err": "Could not save connection."}), 500
  
  return render_template('github_callback_success.html', connection_details=connection_details_for_frontend)