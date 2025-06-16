# --- Helper to serialize SQLAlchemy objects (basic version) ---
def serialize_definitions(definitions):
    """Serializes TriggerDefinition or ActionDefinition objects."""
    serialized = []
    for definition in definitions:
        data = {
            "id": definition.id,
            "key": definition.key,
            "display_name": definition.display_name,
            "description": definition.description,
            "auth_type": definition.auth_type,
            "config_schema": definition.connector_config_schema,
            "logo_url": definition.logo_url,
        }
        serialized.append(data)
    return serialized

def serialize_trigger_action_definitions(definitions):
    """Serializes TriggerDefinition or ActionDefinition objects."""
    serialized = []
    for definition in definitions:
        data = {
            "id": definition.id,
            "key": definition.event_key if hasattr(definition, 'event_key') else definition.action_key,
            "display_name": definition.display_name,
            "description": definition.description,
            "config_schema": definition.config_schema,
            "connector_key": definition.connector_definition.key,
            "connector_display_name": definition.connector_definition.display_name
        }
        if hasattr(definition, 'output_schema'):
            data["output_schema"] = definition.output_schema
        if hasattr(definition, 'input_schema'): # For ActionDefinition
            data["input_schema"] = definition.input_schema
        if hasattr(definition, 'requires_webhook_endpoint'): # For TriggerDefinition
            data["requires_webhook_endpoint"] = definition.requires_webhook_endpoint
        serialized.append(data)
    return serialized


# THIS IS A PLACEHOLDER. Use a proper encryption library like 'cryptography'.
# Example using Fernet from cryptography:
from cryptography.fernet import Fernet
import os

# Generate a key ONCE and store it securely (e.g., env variable)
# key = Fernet.generate_key()
# print(key.decode()) # Store this key

ENCRYPTION_KEY = os.environ.get('FERNET_ENCRYPTION_KEY') # Load from environment
if not ENCRYPTION_KEY:
    raise ValueError("FERNET_ENCRYPTION_KEY not set in environment variables.")

_cipher_suite = Fernet(ENCRYPTION_KEY.encode())

def encrypt_value(value: str) -> str:
    if not value:
        return value
    return _cipher_suite.encrypt(value.encode()).decode()

def decrypt_value(encrypted_value: str) -> str:
    if not encrypted_value:
        return encrypted_value
    return _cipher_suite.decrypt(encrypted_value.encode()).decode()

# --- Simple Pass-through (NOT SECURE FOR PRODUCTION) ---
# Remove above and uncomment below if you want to run without real encryption temporarily
# def encrypt_value(value: str) -> str:
#     print("WARNING: Encryption is disabled. Do not use in production.")
#     return value

# def decrypt_value(encrypted_value: str) -> str:
#     print("WARNING: Decryption is disabled. Do not use in production.")
#     return encrypted_value
