from typing import List, Optional
from flask_sqlalchemy.session import Session

from project.domain.models.connector import Connector as DomainConnector, AuthType
from project.domain.models.connector import ActionType, TriggerType
from project.domain.repositories.connector_repository import IConnectorRepository
from project.infrastructure.models.connector import Connector as SQLConnector


class SQLAlchemyConnectorRepository(IConnectorRepository):
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_key(self, key: str) -> Optional[DomainConnector]:
        sql_connector = (
            self.session.query(SQLConnector)
            .filter_by(key=key)
            .one_or_none()
        )
        if not sql_connector:
            return None
        
        return ConnectorMapper.to_domain(sql_connector)
    
    def list_all(self) -> List[DomainConnector]:
        sql_connectors = self.session.query(SQLConnector).order_by(SQLConnector.display_name).all()
        return [ConnectorMapper.to_domain(c, False) for c in sql_connectors]


class ConnectorMapper:
    @staticmethod
    def to_domain(sql_connector: SQLConnector, include_relations: bool = True) -> DomainConnector:
        return DomainConnector(
            id=sql_connector.id,
            key=sql_connector.key,
            display_name=sql_connector.display_name,
            description=sql_connector.description,
            auth_type=AuthType(sql_connector.auth_type) if sql_connector.auth_type else None,
            logo_url=sql_connector.logo_url,
            trigger_types=[
                TriggerType(
                    id=t.id,
                    event_key=t.event_key,
                    display_name=t.display_name,
                    description=t.description,
                    config_schema=t.config_schema,
                    output_schema=t.output_schema
                )
                for t in sql_connector.trigger_definitions
            ] if include_relations else [],
            action_types=[
                ActionType(
                    id=a.id,
                    action_key=a.action_key,
                    display_name=a.display_name,
                    description=a.description,
                    config_schema=a.config_schema,
                    input_schema=a.input_schema,
                    output_schema=a.output_schema
                )
                for a in sql_connector.action_definitions
            ] if include_relations else []
        )

    @staticmethod
    def from_domain(domain_connector: DomainConnector, sql_connector: SQLConnector):
        pass