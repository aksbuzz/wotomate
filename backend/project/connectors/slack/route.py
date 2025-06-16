import os
import secrets
from project import db
import requests
from project.models import Connector
from project.utils import encrypt_value
from urllib.parse import urlencode
from flask import Blueprint, current_app, jsonify, render_template, request, session
from flask_jwt_extended import get_jwt_identity, jwt_required


SLACK_CLIENT_ID = os.getenv('SLACK_CLIENT_ID')
SLACK_CLIENT_SECRET = os.getenv('SLACK_CLIENT_SECRET')
SLACK_REDIRECT_URI = os.getenv('SLACK_REDIRECT_URI', 'http://localhost:5000/api/connection/slack/callback')

slack_auth_bp = Blueprint('slack_auth_bp', __name__)

@slack_auth_bp.route('/initiate', methods=['GET'])
@jwt_required()
def slack_connect_initiate():
  state = secrets.token_urlsafe(16)
  session['oauth_state_github'] = state

  