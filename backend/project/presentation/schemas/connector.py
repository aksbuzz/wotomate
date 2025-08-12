from marshmallow import Schema, fields

class TriggerTypeSchema(Schema):
    id = fields.Int(dump_only=True)
    event_key = fields.Str(required=True)
    display_name = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    config_schema = fields.Dict(dump_only=True)
    output_schema = fields.Dict(dump_only=True)

class ActionTypeSchema(Schema):
    id = fields.Int(dump_only=True)
    action_key = fields.Str(required=True)
    display_name = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    config_schema = fields.Dict(dump_only=True)
    input_schema = fields.Dict(dump_only=True)
    output_schema = fields.Dict(dump_only=True)

class ConnectorSchema(Schema):
    id = fields.Int(dump_only=True)
    key = fields.Str(dump_only=True)
    display_name = fields.Str(dump_only=True)
    description = fields.Str(allow_none=True)
    auth_type = fields.Str(allow_none=True)
    logo_url = fields.Url(allow_none=True)

class ConnectorDetailSchema(Schema):
    id = fields.Int(dump_only=True)
    key = fields.Str(dump_only=True)
    display_name = fields.Str(dump_only=True)
    description = fields.Str(allow_none=True)
    auth_type = fields.Str(allow_none=True)
    logo_url = fields.Url(allow_none=True)
    trigger_types = fields.List(fields.Nested(TriggerTypeSchema), dump_only=True)
    action_types = fields.List(fields.Nested(ActionTypeSchema), dump_only=True)

class ConnectionSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(dump_only=True)
    connector_key = fields.Str(dump_only=True)
    connection_name = fields.Str(allow_none=True)
    status = fields.Str(dump_only=True)
    created_at = fields.Str(dump_only=True)
    updated_at = fields.Str(dump_only=True)

class ConnectionCreateSchema(Schema):
    connector_key = fields.Str(required=True, description="The key of the connector to use.")
    connection_name = fields.Str(required=True, description="A unique name for this connection.")
    credentials = fields.Dict(required=True, description="Credentials for the connection.", load_only=True)
