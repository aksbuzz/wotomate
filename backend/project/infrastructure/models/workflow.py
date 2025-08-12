from project import db
from datetime import datetime


class Workflow(db.Model):
    __tablename__ = 'workflow'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    owner = db.relationship('User', back_populates='workflows')
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    status = db.Column(db.String(100), nullable=False) # draft, published
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    trigger = db.relationship(
        'Trigger', uselist=False, back_populates='workflow', cascade='all, delete-orphan'
    )
    actions = db.relationship(
        'Action', back_populates='workflow', 
        order_by='Action.position', cascade='all, delete-orphan', lazy='dynamic'
    )
    runs = db.relationship('WorkflowRun', back_populates='workflow', lazy='dynamic')
