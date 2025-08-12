from project import db


class TriggerType(db.Model):
    __tablename__ = 'trigger_definition'
    
    id = db.Column(db.Integer, primary_key=True)
    connector_definition_id = db.Column(db.Integer, db.ForeignKey('connector_definition.id'), nullable=False)
    event_key = db.Column(db.String(100), nullable=False)
    display_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    config_schema = db.Column(db.JSON, nullable=False)
    output_schema = db.Column(db.JSON, nullable=False)

    # Relationships
    connector_definition = db.relationship('ConnectorDefinition', back_populates='trigger_definitions')
    
    # Constraints
    __table_args__ = (
        db.UniqueConstraint('connector_definition_id', 'event_key', name='_connector_event_key_uc'),
    )

    def __repr__(self):
        return f'<TriggerDefinition {self.connector_definition.key if self.connector_definition else "None"}.{self.event_key}>'
