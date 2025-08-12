from typing import Optional

from project.domain.models.connection import Connection
from project.domain.repositories.connector_repository import IConnectorRepository
from project.domain.repositories.connection_repository import IConnectionRepository
from project.application.services import IEncryptionService, IUnitOfWork

class ConnectionUseCases:
    def __init__(
        self,
        connection_repository: IConnectionRepository,
        connector_repository: IConnectorRepository,
        encryption_service: IEncryptionService,
        uow: IUnitOfWork
    ):
        self.connection_repository = connection_repository
        self.connector_repository = connector_repository
        self.encryption_service = encryption_service
        self.uow = uow

    def create(self, user_id: int, connector_key: str, raw_credentials: dict, connection_name: Optional[str] = None):
        with self.uow:
            connector = self.connector_repository.get_by_key(connector_key)
            if not connector:
                raise ValueError(f"Connector '{connector_key}' not found.")

            existing_connection = self.connection_repository.find_by_user_and_connector(user_id, connector_key)
            if existing_connection:
                raise ValueError(f"User already has a connection for connector '{connector_key}'")
            
            encryption_creds = self.encryption_service.encrypt(raw_credentials)

            new_connection = Connection.create(
                user_id=user_id,
                connector_key=connector_key,
                credentials=encryption_creds,
                connection_name=connection_name
            )

            self.connection_repository.save(new_connection)
            self.uow.commit()

    def list_by_user(self, user_id: int):
        connections = self.connection_repository.find_by_user(user_id)

        return [
            {
                'id': c.id,
                'connector_key': c.connector_key,
                'connection_name': c.connection_name,
                'status': c.status.value,
                'created_at': c.created_at.isoformat(),
                'is_usable': c.is_usable(),
            }
            for c in connections
        ]
    
    def delete(self, connection_id: int, user_id: int):
        with self.uow:
            connection = self.connection_repository.get_by_id(connection_id)
            if not connection:
                raise ValueError("Connection not found")
            
            if connection.user_id != user_id:
                raise PermissionError("User is not authorized to delete this connection")
            
            connection.revoke()

            self.connection_repository.save(connection)
            self.uow.commit()