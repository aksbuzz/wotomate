from project import db
from datetime import datetime


class Connector(db.Model):
    __tablename__ = 'connector'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', back_populates='connectors')
    # This should correspond to ConnectorDefinition.key
    connector_key = db.Column(db.String(50), nullable=False)
    # Name given by user for this specific connection, e.g., "My Work Google Drive"
    connection_name = db.Column(db.String(100), nullable=True)
    credentials = db.Column(db.JSON, nullable=False) # Encrypt sensitive parts
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    __table_args__ = (
        # User can have multiple connections to the same service type if they name them differently
        # Or, if connection_name is not used, service_key should be unique per user.
        # Let's assume a user connects a "service type" (service_key) once,
        # unless they provide distinct connection_names for multiple accounts of the same service.
        # For simplicity now: one connection per service_key per user.
        db.UniqueConstraint('user_id', 'connector_key', name='_user_connector_key_uc'),
    )