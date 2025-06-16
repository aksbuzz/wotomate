from project import db


class ConnectorDefinition(db.Model):
    __tablename__ = 'connector_definition'
    id = db.Column(db.Integer, primary_key=True)
    # Unique key for the connector, e.g., "google_drive", "github", "webhook_connector"
    key = db.Column(db.String(50), unique=True, nullable=False, index=True)
    display_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    # E.g., "oauth2", "api_key", "none" - for UI hints or auth flow logic
    auth_type = db.Column(db.String(50), nullable=True)
    # Optional: JSON schema for any connector-wide configuration needed beyond ConnectedService
    connector_config_schema = db.Column(db.JSON, nullable=True)
    logo_url = db.Column(db.String(255), nullable=True) # For UI

    trigger_definitions = db.relationship('TriggerDefinition', back_populates='connector_definition', lazy='dynamic')
    action_definitions = db.relationship('ActionDefinition', back_populates='connector_definition', lazy='dynamic')

    def __repr__(self):
        return f'<ConnectorDefinition {self.key}>'