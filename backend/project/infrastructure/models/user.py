from project import db
from datetime import datetime


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    workflows = db.relationship('Workflow', back_populates='owner', lazy=True)
    connectors = db.relationship('Connector', back_populates='user', lazy=True)

    def __repr__(self):
        return f'<User {self.email}>'