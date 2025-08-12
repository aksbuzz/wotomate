from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

from project.presentation.schemas.error import ErrorSchema
from project.presentation.schemas.connector import ConnectorSchema, ConnectorDetailSchema
from project.application.use_cases.connector import ConnectorUseCases

from project.infrastructure.repositories.connector_repository import SQLAlchemyConnectorRepository
from project.infrastructure.services.uow import SQLAlchemyUnitOfWork

connectors_bp = Blueprint('auth_api', __name__, url_prefix='/connectors')

uow = SQLAlchemyUnitOfWork()

connector_repository = SQLAlchemyConnectorRepository(uow.session)
connector_use_cases = ConnectorUseCases(connector_repository)

@connectors_bp.route('', methods=['GET'])
@jwt_required()
def list_connectors():
    try:
        connectors = connector_use_cases.list_all()
        return jsonify(ConnectorSchema.dump(connectors)), 200

    except ValueError as e:
        error = {'error': 'Invalid Request', 'message': str(e)}
        return jsonify(ErrorSchema.dump(error)), 400
    except Exception as e:
        error = {'error': 'Internal Error', 'message': 'An unexpected error occurred'}
        return jsonify(ErrorSchema.dump(error)), 500


@connectors_bp.route('/<string:connector_key>', methods=['GET'])
@jwt_required()
def get_connector_details(connector_key):
    try:
        connector = connector_use_cases.get_by_key(connector_key)
        if not connector:
            error = {'error': 'Not Found', 'message': f'Connector {connector_key} not found'}
            return jsonify(ErrorSchema.dump(error)), 404
        
        return jsonify(ConnectorDetailSchema.dump(connector))
    
    except ValueError as e:
        error = {'error': 'Invalid Request', 'message': str(e)}
        return jsonify(ErrorSchema.dump(error)), 400
    except Exception as e:
        error = {'error': 'Internal Error', 'message': 'An unexpected error occurred'}
        return jsonify(ErrorSchema.dump(error)), 500