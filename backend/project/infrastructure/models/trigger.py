from project import db
from datetime import datetime, timedelta


class Trigger(db.Model):
    __tablename__ = 'trigger'
    id = db.Column(db.Integer, primary_key=True)
    workflow_id = db.Column(db.Integer, db.ForeignKey('workflow.id', ondelete='CASCADE'), nullable=False)
    workflow = db.relationship('Workflow', back_populates='trigger')
    
    trigger_definition_id = db.Column(db.Integer, db.ForeignKey('trigger_definition.id'), nullable=False)
    trigger_definition = db.relationship('TriggerDefinition', lazy='joined') # Often needed with the trigger
    
    config = db.Column(db.JSON, nullable=True) # User-specific config for this trigger instance
    
    # Link to Connector if this trigger needs authentication
    connector_id = db.Column(db.Integer, db.ForeignKey('connector.id'), nullable=True)
    connector = db.relationship('Connector')
    
    last_polled_at = db.Column(db.DateTime, nullable=True)
    polling_state = db.Column(db.JSON, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def should_poll(self):
        if not self.last_polled_at:
            return True
        
        next_poll_time = self.last_polled_at + timedelta(minutes=5)
        return datetime.utcnow() >= next_poll_time
