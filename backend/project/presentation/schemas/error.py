from marshmallow import Schema, fields

class ErrorSchema(Schema):
    error = fields.Str(required=True)
    message = fields.Str(required=True)