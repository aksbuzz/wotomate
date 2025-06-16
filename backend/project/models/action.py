from project import db
from datetime import datetime


class Action(db.Model):
    __tablename__ = 'action'
    id = db.Column(db.Integer, primary_key=True)
    workflow_id = db.Column(db.Integer, db.ForeignKey('workflow.id', ondelete='CASCADE'), nullable=False)
    workflow = db.relationship('Workflow', back_populates='actions')
    
    action_definition_id = db.Column(db.Integer, db.ForeignKey('action_definition.id'), nullable=False)
    action_definition = db.relationship('ActionDefinition', lazy='joined') # Often needed with the action
    
    position = db.Column(db.Integer, nullable=False) # Order of execution
    config = db.Column(db.JSON, nullable=False) # User-specific config for this action instance
    
    # Link to Connector if this action needs authentication
    connector_id = db.Column(db.Integer, db.ForeignKey('connector.id'), nullable=True)
    connector = db.relationship('Connector')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('workflow_id', 'position', name='_action_position_uc'),
    )