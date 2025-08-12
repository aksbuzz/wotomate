from project import db
from datetime import datetime


class Connection(db.Model):
    __tablename__ = 'connector'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    connector_key = db.Column(db.String(50), nullable=False)
    connection_name = db.Column(db.String(100), nullable=True)
    credentials = db.Column(db.JSON, nullable=False)
    status=db.Columb(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', back_populates='connectors')
    
    # Constraints
    __table_args__ = (
        # one connection per connector_key per user.
        db.UniqueConstraint('user_id', 'connector_key', name='_user_connector_key_uc'),
    )