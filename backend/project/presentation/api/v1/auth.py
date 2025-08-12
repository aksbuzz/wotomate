from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from project.presentation.schemas.auth import RegisterSchema, LoginSchema, AuthResponseSchema, UserSchema
from project.presentation.schemas.error import ErrorSchema

from project.application.use_cases.auth import AuthUseCases

from project.infrastructure.security.hashing import BCryptPasswordHasher
from project.infrastructure.repositories.user_repository import SQLAlchemyUserRepository
from project.infrastructure.services.uow import SQLAlchemyUnitOfWork

auth_bp = Blueprint('auth_api', __name__, url_prefix='/auth')

password_hasher = BCryptPasswordHasher()
uow = SQLAlchemyUnitOfWork()

user_repository = SQLAlchemyUserRepository(uow.session)
auth_use_cases = AuthUseCases(user_repository, password_hasher, uow)

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        errors = RegisterSchema().validate(data)
        if errors:
            return jsonify(errors), 400
    
        auth_use_cases.register(data)
        return jsonify({'status': 'ok'}), 203
    
    except ValueError as e:
        error = {'error': 'Invalid Request', 'message': str(e)}
        return jsonify(ErrorSchema.dump(error)), 400
    except Exception as e:
        error = {'error': 'Internal Error', 'message': 'An unexpected error occurred'}
        return jsonify(ErrorSchema.dump(error)), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        errors = LoginSchema().validate(data)
        if errors:
            return jsonify(errors), 400
        
        result = auth_use_cases.login(data)
        return AuthResponseSchema().dump(result), 200
    
    except ValueError as e:
        error = {'error': 'Invalid Request', 'message': str(e)}
        return jsonify(ErrorSchema.dump(error)), 400
    except Exception as e:
        error = {'error': 'Internal Error', 'message': 'An unexpected error occurred'}
        return jsonify(ErrorSchema.dump(error)), 500


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    try:
        current_user_id = get_jwt_identity()
        user = auth_use_cases.get_user_by_id(current_user_id)
        if not user:
            return jsonify({"err": "User not found"}), 404
        return UserSchema().dump(user), 200
    
    except ValueError as e:
        error = {'error': 'Invalid Request', 'message': str(e)}
        return jsonify(ErrorSchema.dump(error)), 400
    except Exception as e:
        error = {'error': 'Internal Error', 'message': 'An unexpected error occurred'}
        return jsonify(ErrorSchema.dump(error)), 500