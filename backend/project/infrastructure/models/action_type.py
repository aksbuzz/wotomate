from project import db


class ActionType(db.Model):
    __tablename__ = 'action_definition'
    
    id = db.Column(db.Integer, primary_key=True)
    connector_definition_id = db.Column(db.Integer, db.ForeignKey('connector_definition.id'), nullable=False)
    action_key = db.Column(db.String(100), nullable=False)
    display_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    config_schema = db.Column(db.JSON, nullable=False)
    input_schema = db.Column(db.JSON, nullable=True)
    output_schema = db.Column(db.JSON, nullable=False)

    # Relationships
    connector_definition = db.relationship('ConnectorDefinition', back_populates='action_definitions')
    
    # Constraints
    __table_args__ = (
        db.UniqueConstraint('connector_definition_id', 'action_key', name='_connector_action_key_uc'),
    )

    def __repr__(self):
        return f'<ActionDefinition {self.connector_definition.key if self.connector_definition else "None"}.{self.action_key}>'

