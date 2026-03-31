# schemas/auth_schema.py
from marshmallow import Schema, fields, validate, validates, ValidationError
import re


class RegisterSchema(Schema):
    """Validates user registration input."""
    full_name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    email     = fields.Email(required=True)
    password  = fields.Str(required=True, validate=validate.Length(min=6, max=128))

    @validates('password')
    def validate_password_strength(self, value):
        """Password must contain at least one letter and one number."""
        if not re.search(r'[A-Za-z]', value) or not re.search(r'[0-9]', value):
            raise ValidationError('Password must contain at least one letter and one number')


class LoginSchema(Schema):
    """Validates login credentials."""
    email    = fields.Email(required=True)
    password = fields.Str(required=True)
