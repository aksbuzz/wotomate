from flask import Blueprint, request, jsonify
from project import db
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from project.models import User

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'err': 'Email and password are required'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'err': 'User already exists'}), 400

    new_user = User(email=email)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'msg': 'User created successfully'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'err': 'Email and password are required'}), 400

    user = User.query.filter_by(email=email).first()

    if user and user.check_password(password):
        access_token = create_access_token(identity=str(user.id), expires_delta=False)
        return jsonify(access_token=access_token, user_id=user.id, email=email), 200
    else:
        return jsonify({'err': 'Invalid credentials'}), 401
    

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({"err": "User not found"}), 404
    return jsonify(id=user.id, email=user.email), 200
