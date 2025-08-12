from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from project.presentation.schemas.error import ErrorSchema
from project.presentation.schemas.connector import ConnectionCreateSchema, ConnectionSchema
from project.application.use_cases.connection import ConnectionUseCases

from project.infrastructure.repositories.connection_repository import SQLAlchemyConnectionRepository
from project.infrastructure.repositories.connector_repository import SQLAlchemyConnectorRepository
from project.infrastructure.security.encryption import CryptographyEncryptionService
from project.infrastructure.services.uow import SQLAlchemyUnitOfWork

connections_bp = Blueprint('auth_api', __name__, url_prefix='/connections')

uow = SQLAlchemyUnitOfWork()
# TODO: add key
encryption_service = CryptographyEncryptionService()
connector_repository = SQLAlchemyConnectorRepository(uow.session)
connection_repository = SQLAlchemyConnectionRepository(uow.session)

connection_use_cases = ConnectionUseCases(connection_repository, connector_repository, encryption_service, uow)

@connections_bp.route('', methods=['GET'])
@jwt_required()
def list_connections():
    try:
        current_user_id = get_jwt_identity()
        connections = connection_use_cases.list_by_user(user_id=current_user_id)
        return jsonify(ConnectionSchema.dump(connections)), 200

    except ValueError as e:
        error = {'error': 'Invalid Request', 'message': str(e)}
        return jsonify(ErrorSchema.dump(error)), 400
    except Exception as e:
        error = {'error': 'Internal Error', 'message': 'An unexpected error occurred'}
        return jsonify(ErrorSchema.dump(error)), 500


@connections_bp.route('/<int:connection_id>', methods=['GET'])
@jwt_required()
def delete_connection(connection_id):
    try:
        current_user_id = get_jwt_identity()
        connection = connection_use_cases.delete(connection_id=connection_id, user_id=current_user_id)      
        
        return jsonify(ConnectionSchema.dump(connection))
    
    except PermissionError as e:
        error = {'error': 'Forbidden', 'message': str(e)}
        return jsonify(ErrorSchema.dump(error)), 403
    except ValueError as e:
        error = {'error': 'Invalid Request', 'message': str(e)}
        return jsonify(ErrorSchema.dump(error)), 400
    except Exception as e:
        error = {'error': 'Internal Error', 'message': 'An unexpected error occurred'}
        return jsonify(ErrorSchema.dump(error)), 500