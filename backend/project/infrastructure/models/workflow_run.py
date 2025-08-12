from project import db
from datetime import datetime

class WorkflowRun(db.Model):
    __tablename__ = 'workflow_run'
    id = db.Column(db.Integer, primary_key=True)
    workflow_id = db.Column(db.Integer, db.ForeignKey('workflow.id', ondelete='CASCADE'), nullable=False)
    workflow = db.relationship('Workflow', back_populates='runs')
    
    status = db.Column(db.String(100), nullable=False)
    trigger_event_data = db.Column(db.JSON, nullable=True) # Data received from the trigger
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    finished_at = db.Column(db.DateTime, nullable=True)
    
    # Denormalize trigger info for easier log access if needed, or rely on workflow.trigger
    # For example, could store workflow_trigger_id if trigger config can change.
    # trigger_output renamed to trigger_event_data for clarity

    actions_results = db.relationship( # Renamed for clarity
        'WorkflowRunAction', back_populates='run', cascade='all, delete-orphan',
        order_by='WorkflowRunAction.position', lazy='dynamic'
    )