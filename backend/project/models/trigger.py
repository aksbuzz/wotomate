from project import db
from datetime import datetime, timedelta
import uuid
from .trigger_definition import TriggerDefinition


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
    
    webhook_id = db.Column(db.String(36), unique=True, nullable=True, index=True)
    
    last_polled_at = db.Column(db.DateTime, nullable=True)
    polling_state = db.Column(db.JSON, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def should_poll(self):
        if not self.last_polled_at:
            return True
        
        next_poll_time = self.last_polled_at + timedelta(minutes=5)
        return datetime.utcnow() >= next_poll_time

    def _ensure_webhook_id(self):
        """
        Ensures webhook_id is set if the trigger_definition requires it,
        and clears it if not required.
        Relies on self.trigger_definition being populated.
        """
        if self.trigger_definition:
            if self.trigger_definition.requires_webhook_endpoint:
                if not self.webhook_id:
                    self.webhook_id = str(uuid.uuid4())
            elif self.webhook_id: # Not required, but webhook_id exists
                self.webhook_id = None # Clear it
        # If trigger_definition is None (e.g., ID set but object not loaded yet),
        # this method won't operate correctly. Caller should ensure it's loaded.

@db.event.listens_for(Trigger, 'before_insert')
@db.event.listens_for(Trigger, 'before_update')
def on_trigger_before_save(mapper, connection, target: Trigger):
    """
    Handles webhook_id generation/clearing.
    """
    target._ensure_webhook_id()