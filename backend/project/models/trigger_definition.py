from project import db


class TriggerDefinition(db.Model):
    __tablename__ = 'trigger_definition'
    id = db.Column(db.Integer, primary_key=True)
    connector_definition_id = db.Column(db.Integer, db.ForeignKey('connector_definition.id'), nullable=False)
    connector_definition = db.relationship('ConnectorDefinition', back_populates='trigger_definitions')
    
    # Specific event key within the connector, e.g., "new_file", "commit_pushed"
    event_key = db.Column(db.String(100), nullable=False)
    display_name = db.Column(db.String(100), nullable=False) # E.g., "New File in Google Drive Folder"
    description = db.Column(db.Text, nullable=True)
    config_schema = db.Column(db.JSON, nullable=False) # JSON schema for user-provided config
    output_schema = db.Column(db.JSON, nullable=False) # JSON schema for data this trigger outputs
    # True if this trigger type inherently requires a webhook endpoint (e.g., generic inbound webhook)
    requires_webhook_endpoint = db.Column(db.Boolean, default=False, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('connector_definition_id', 'event_key', name='_connector_event_key_uc'),
    )

    def __repr__(self):
        return f'<TriggerDefinition {self.connector_definition.key if self.connector_definition else "None"}.{self.event_key}>'
