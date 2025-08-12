from marshmallow import Schema, fields

class RegisterSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)

class AuthResponseSchema(Schema):
    access_token = fields.Str()
    user_id = fields.Int()
    email = fields.Email()

class UserSchema(Schema):
    id = fields.Int()
    email = fields.Email()