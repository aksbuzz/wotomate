from project.domain.repositories.connector_repository import IConnectorRepository


class ConnectorUseCases:
    def __init__(self, connector_repository: IConnectorRepository):
        self.connector_repository = connector_repository

    def list_all(self):
        connectors = self.connector_repository.list_all()
        return [
            {
                'id': c.id,
                'key': c.key,
                'display_name': c.display_name,
                'description': c.description,
                'auth_type': c.auth_type.value if c.auth_type else None,
                'logo_url': c.logo_url
            }
            for c in connectors
        ]
    
    def get_by_key(self, key: str):
        connector = self.connector_repository.get_by_key(key)
        if not connector:
            return None
        
        return {
            'id': connector.id,
            'key': connector.key,
            'display_name': connector.display_name,
            'description': connector.description,
            'auth_type': connector.auth_type.value if connector.auth_type else None,
            'logo_url': connector.logo_url,
            'trigger_types': [
                {
                    'id': t.id,
                    'trigger_key': t.event_key,
                    'display_name': t.display_name,
                    'description': t.description,
                    'config_schema': t.config_schema,
                    'output_schema': t.output_schema
                }
                for t in connector.trigger_types
            ],
            'action_types': [
                {
                    'id': a.id,
                    'action_key': a.action_key,
                    'display_name': a.display_name,
                    'description': a.description,
                    'config_schema': a.config_schema,
                    'input_schema': a.input_schema,
                    'output_schema': a.output_schema
                }
                for a in connector.action_types
            ]
        }