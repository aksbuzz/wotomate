from project import db


class ActionDefinition(db.Model):
    __tablename__ = 'action_definition'
    id = db.Column(db.Integer, primary_key=True)
    connector_definition_id = db.Column(db.Integer, db.ForeignKey('connector_definition.id'), nullable=False)
    connector_definition = db.relationship('ConnectorDefinition', back_populates='action_definitions')

    # Specific action key within the connector, e.g., "add_row", "send_message"
    action_key = db.Column(db.String(100), nullable=False)
    display_name = db.Column(db.String(100), nullable=False) # E.g., "Add Row to Google Sheet"
    description = db.Column(db.Text, nullable=True)
    config_schema = db.Column(db.JSON, nullable=False) # JSON schema for user-provided config
    input_schema = db.Column(db.JSON, nullable=True) # JSON schema for data this action expects
    output_schema = db.Column(db.JSON, nullable=False) # JSON schema for data this action outputs

    __table_args__ = (
        db.UniqueConstraint('connector_definition_id', 'action_key', name='_connector_action_key_uc'),
    )

    def __repr__(self):
        return f'<ActionDefinition {self.connector_definition.key if self.connector_definition else "None"}.{self.action_key}>'

