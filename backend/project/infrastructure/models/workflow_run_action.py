from project import db
from datetime import datetime

class WorkflowRunAction(db.Model):
    __tablename__ = 'workflow_run_action'
    id = db.Column(db.Integer, primary_key=True)
    run_id = db.Column(db.Integer, db.ForeignKey('workflow_run.id', ondelete='CASCADE'), nullable=False)
    run = db.relationship('WorkflowRun', back_populates='actions_results') # Matched rename
    
    action_id = db.Column(db.Integer, db.ForeignKey('action.id'), nullable=False) # FK to the configured action
    # Removed direct relationship to Action to avoid potential issues if Action is deleted/modified
    # Storing a copy of definition and config might be safer for historical runs.
    # For now, keeping it simple. If Action is deleted, this link breaks.
    # Consider ondelete='SET NULL' or storing action_definition_id and config snapshot.
    action = db.relationship('Action', lazy='joined') # The specific configured action instance
    
    position = db.Column(db.Integer, nullable=False) # Copied from Action for this run
    status = db.Column(db.String(100), nullable=False)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    finished_at = db.Column(db.DateTime, nullable=True)
    input_data = db.Column(db.JSON, nullable=True) # Data fed into this action for this run
    output_data = db.Column(db.JSON, nullable=True) # Result/output from this action for this run (renamed from 'result')
    log = db.Column(db.Text, nullable=True) # Execution logs/errors