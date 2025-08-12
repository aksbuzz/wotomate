from typing import List, Optional
from flask_sqlalchemy.session import Session

from project.domain.models.connection import Connection as DomainConnection, ConnectionStatus
from project.domain.repositories.connection_repository import IConnectionRepository
from project.infrastructure.models.connection import Connection as SQLConnection

class SQLAlchemyConnectionRepository(IConnectionRepository):
    def __init__(self, session: Session):
        self.session = session
    
    def save(self, connection: DomainConnection) -> None:
        if connection.id:
            # update
            sql_connection = self.session.get(SQLConnection, connection.id)
            if not sql_connection:
                ValueError(f"Connection with {connection.id} not found")
        else:
            # create
            sql_connection = SQLConnection(user_id=connection.user_id)
        
        ConnectionMapper.from_domain(connection, sql_connection)
        self.session.add(sql_connection)
    
    def get_by_id(self, connection_id: int) -> Optional[DomainConnection]:
        sql_connection = self.session.get(SQLConnection, connection_id)
        if not sql_connection:
            return None
        
        return ConnectionMapper.to_domain(sql_connection)
    
    def find_by_user(self, user_id: int) -> List[DomainConnection]:
        sql_connections = (
            self.session.query(SQLConnection)
            .filter_by(user_id=user_id)
            .all()
        )
        
        return [ConnectionMapper.to_domain(c) for c in sql_connections]
    
    def find_by_user_and_connector(self, user_id: int, connector_key: int) -> Optional[DomainConnection]:
        sql_connection = (
            self.session.query(SQLConnection)
            .filter_by(user_id=user_id, connector_key=connector_key)
            .first()
        )
        
        if not sql_connection:
            return None
        
        return ConnectionMapper.to_domain(sql_connection)
    
class ConnectionMapper:
    @staticmethod
    def to_domain(sql_connection: SQLConnection) -> DomainConnection:
        return DomainConnection(
            id = sql_connection.id,
            user_id = sql_connection.user_id,
            connector_key = sql_connection.connector_key,
            connection_name = sql_connection.connection_name,
            status = ConnectionStatus(sql_connection.status),
            created_at = sql_connection.created_at,
            updated_at = sql_connection.updated_at,
            credentials = sql_connection.credentials
        )
    
    @staticmethod
    def from_domain(domain_connection: DomainConnection, sql_connection: SQLConnection):
        sql_connection.user_id = domain_connection.user_id
        sql_connection.connector_key = domain_connection.connector_key
        sql_connection.connection_name = domain_connection.connection_name
        sql_connection.status = domain_connection.status.value if isinstance(domain_connection.status, ConnectionStatus) else domain_connection.status
        sql_connection.created_at = domain_connection.created_at
        sql_connection.updated_at = domain_connection.updated_at
        sql_connection.credentials = domain_connection.credentials