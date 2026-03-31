# middleware/validation_middleware.py
from functools import wraps
from flask import request, jsonify
from marshmallow import ValidationError


def validate_body(schema_class):
    """
    Decorator: validates request JSON body against a Marshmallow schema.
    Injects validated data as `validated_data` keyword argument.

    Usage:
        @validate_body(RegisterSchema)
        def register(validated_data):
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            schema = schema_class()
            json_data = request.get_json(silent=True)
            if json_data is None:
                return jsonify({
                    "status": "error",
                    "message": "Request body must be JSON"
                }), 400
            try:
                validated = schema.load(json_data)
            except ValidationError as err:
                return jsonify({
                    "status": "error",
                    "message": "Validation failed",
                    "errors": err.messages
                }), 400
            return f(*args, validated_data=validated, **kwargs)
        return decorated
    return decorator
