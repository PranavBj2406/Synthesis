# app/middleware/validation.py
from functools import wraps
from flask import request, jsonify,current_app
import json

def validate_json(f):
    """
    Decorator to ensure request contains valid JSON data.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # Check if request has JSON content type
        if not request.is_json:
            return jsonify({
                'success': False,
                'message': 'Request must be JSON format with Content-Type: application/json'
            }), 400
        
        # Check if JSON data exists
        try:
            data = request.get_json()
            if data is None:
                return jsonify({
                    'success': False,
                    'message': 'Request body must contain valid JSON data'
                }), 400
        except Exception as e:
            return jsonify({
                'success': False,
                'message': 'Invalid JSON format in request body',
                'error': str(e)
            }), 400
        
        return f(*args, **kwargs)
    
    return decorated


def validate_required_fields(required_fields):
    """
    Decorator to validate that required fields are present in request JSON.
    
    Args:
        required_fields (list): List of required field names
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'message': 'Request body is required'
                }), 400
            
            missing_fields = []
            empty_fields = []
            
            for field in required_fields:
                if field not in data:
                    missing_fields.append(field)
                elif not data[field] or (isinstance(data[field], str) and data[field].strip() == ''):
                    empty_fields.append(field)
            
            if missing_fields:
                return jsonify({
                    'success': False,
                    'message': f'Missing required fields: {", ".join(missing_fields)}'
                }), 400
            
            if empty_fields:
                return jsonify({
                    'success': False,
                    'message': f'The following fields cannot be empty: {", ".join(empty_fields)}'
                }), 400
            
            return f(*args, **kwargs)
        
        return decorated
    return decorator


def validate_field_types(field_types):
    """
    Decorator to validate field types in request JSON.
    
    Args:
        field_types (dict): Dictionary with field names as keys and expected types as values
                           e.g., {'name': str, 'age': int, 'is_active': bool}
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'message': 'Request body is required'
                }), 400
            
            type_errors = []
            
            for field, expected_type in field_types.items():
                if field in data and data[field] is not None:
                    if not isinstance(data[field], expected_type):
                        type_name = expected_type.__name__
                        actual_type = type(data[field]).__name__
                        type_errors.append(
                            f'{field} must be of type {type_name}, got {actual_type}'
                        )
            
            if type_errors:
                return jsonify({
                    'success': False,
                    'message': 'Field type validation failed',
                    'errors': type_errors
                }), 400
            
            return f(*args, **kwargs)
        
        return decorated
    return decorator


def validate_content_length(max_length=1024*1024):  # 1MB default
    """
    Decorator to validate request content length.
    
    Args:
        max_length (int): Maximum allowed content length in bytes
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if request.content_length and request.content_length > max_length:
                return jsonify({
                    'success': False,
                    'message': f'Request body too large. Maximum size: {max_length} bytes'
                }), 413
            
            return f(*args, **kwargs)
        
        return decorated
    return decorator


def sanitize_input(f):
    """
    Decorator to sanitize string inputs by stripping whitespace and 
    removing potentially harmful characters.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        data = request.get_json()
        
        if data:
            sanitized_data = {}
            for key, value in data.items():
                if isinstance(value, str):
                    # Strip whitespace
                    sanitized_value = value.strip()
                    # Remove null bytes and other control characters
                    sanitized_value = ''.join(char for char in sanitized_value 
                                            if ord(char) >= 32 or char in '\t\n\r')
                    sanitized_data[key] = sanitized_value
                else:
                    sanitized_data[key] = value
            
            # Update request JSON with sanitized data
            request.json = sanitized_data
        
        return f(*args, **kwargs)
    
    return decorated


def handle_request_errors(f):
    """
    Decorator to handle common request processing errors.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        
        except json.JSONDecodeError as e:
            return jsonify({
                'success': False,
                'message': 'Invalid JSON format',
                'error': str(e)
            }), 400
        
        except UnicodeDecodeError as e:
            return jsonify({
                'success': False,
                'message': 'Invalid character encoding',
                'error': str(e)
            }), 400
        
        except ValueError as e:
            return jsonify({
                'success': False,
                'message': 'Invalid data format',
                'error': str(e)
            }), 400
        
        except Exception as e:
            # Log the error for debugging
            current_app.logger.error(f"Unexpected error in request processing: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'An error occurred while processing the request'
            }), 500
    
    return decorated


# Composite decorators for common validation patterns
def validate_auth_request(f):
    """
    Composite decorator for authentication-related requests.
    Validates JSON, content length, and sanitizes input.
    """
    @validate_json
    @validate_content_length(max_length=2048)  # 2KB for auth requests
    @sanitize_input
    @handle_request_errors
    @wraps(f)
    def decorated(*args, **kwargs):
        return f(*args, **kwargs)
    
    return decorated


def validate_registration_request(f):
    """
    Composite decorator specifically for user registration.
    """
    @validate_auth_request
    @validate_required_fields(['username', 'email', 'password'])
    @validate_field_types({
        'username': str,
        'email': str, 
        'password': str,
        'full_name': str  # Optional field
    })
    @wraps(f)
    def decorated(*args, **kwargs):
        return f(*args, **kwargs)
    
    return decorated


def validate_login_request(f):
    """
    Composite decorator specifically for user login.
    """
    @validate_auth_request
    @validate_required_fields(['email', 'password'])
    @validate_field_types({
        'email': str,
        'password': str
    })
    @wraps(f)
    def decorated(*args, **kwargs):
        return f(*args, **kwargs)
    
    return decorated