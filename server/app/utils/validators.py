import re
from functools import wraps
from flask import request, jsonify
from typing import Dict, List, Any, Optional

class ValidationError(Exception):
    """Custom validation error"""
    def __init__(self, message: str, field: str = None, code: str = None):
        self.message = message
        self.field = field
        self.code = code
        super().__init__(self.message)

class RequestValidator:
    """Request data validation utility class"""
    
    @staticmethod
    def validate_required_fields(data: dict, required_fields: list) -> Dict[str, Any]:
        """
        Validate that all required fields are present and not empty
        
        Args:
            data (dict): Data to validate
            required_fields (list): List of required field names
            
        Returns:
            dict: Validation result
        """
        missing_fields = []
        empty_fields = []
        
        for field in required_fields:
            if field not in data:
                missing_fields.append(field)
            elif not data[field] or (isinstance(data[field], str) and not data[field].strip()):
                empty_fields.append(field)
        
        errors = []
        if missing_fields:
            errors.append({
                'field': 'general',
                'message': f"Missing required fields: {', '.join(missing_fields)}",
                'code': 'MISSING_FIELDS'
            })
        
        if empty_fields:
            errors.append({
                'field': 'general', 
                'message': f"Empty fields not allowed: {', '.join(empty_fields)}",
                'code': 'EMPTY_FIELDS'
            })
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    @staticmethod
    def validate_email(email: str) -> Dict[str, Any]:
        """
        Validate email format
        
        Args:
            email (str): Email to validate
            
        Returns:
            dict: Validation result
        """
        if not email or not isinstance(email, str):
            return {
                'valid': False,
                'error': 'Email is required',
                'code': 'EMAIL_REQUIRED'
            }
        
        email = email.strip()
        
        # Basic email regex pattern
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(email_pattern, email):
            return {
                'valid': False,
                'error': 'Invalid email format',
                'code': 'INVALID_EMAIL_FORMAT'
            }
        
        # Check email length
        if len(email) > 254:  # RFC 5321 limit
            return {
                'valid': False,
                'error': 'Email address is too long',
                'code': 'EMAIL_TOO_LONG'
            }
        
        # Check for common invalid patterns
        if '..' in email or email.startswith('.') or email.endswith('.'):
            return {
                'valid': False,
                'error': 'Invalid email format',
                'code': 'INVALID_EMAIL_PATTERN'
            }
        
        return {'valid': True}
    
    @staticmethod
    def validate_username(username: str) -> Dict[str, Any]:
        """
        Validate username format and requirements
        
        Args:
            username (str): Username to validate
            
        Returns:
            dict: Validation result
        """
        if not username or not isinstance(username, str):
            return {
                'valid': False,
                'error': 'Username is required',
                'code': 'USERNAME_REQUIRED'
            }
        
        username = username.strip()
        
        # Length validation
        if len(username) < 3:
            return {
                'valid': False,
                'error': 'Username must be at least 3 characters long',
                'code': 'USERNAME_TOO_SHORT'
            }
        
        if len(username) > 20:
            return {
                'valid': False,
                'error': 'Username must be less than 20 characters',
                'code': 'USERNAME_TOO_LONG'
            }
        
        # Character validation (alphanumeric and underscores only)
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return {
                'valid': False,
                'error': 'Username can only contain letters, numbers, and underscores',
                'code': 'INVALID_USERNAME_CHARACTERS'
            }
        
        # Cannot start with number
        if username[0].isdigit():
            return {
                'valid': False,
                'error': 'Username cannot start with a number',
                'code': 'USERNAME_STARTS_WITH_NUMBER'
            }
        
        # Reserved usernames
        reserved_usernames = [
            'admin', 'administrator', 'root', 'system', 'user', 'guest',
            'api', 'www', 'mail', 'email', 'support', 'help', 'info',
            'noreply', 'no-reply', 'postmaster', 'webmaster'
        ]
        
        if username.lower() in reserved_usernames:
            return {
                'valid': False,
                'error': 'Username is reserved and cannot be used',
                'code': 'USERNAME_RESERVED'
            }
        
        return {'valid': True}
    
    @staticmethod
    def validate_password(password: str) -> Dict[str, Any]:
        """
        Validate password strength
        
        Args:
            password (str): Password to validate
            
        Returns:
            dict: Validation result
        """
        if not password or not isinstance(password, str):
            return {
                'valid': False,
                'error': 'Password is required',
                'code': 'PASSWORD_REQUIRED'
            }
        
        # Length validation
        if len(password) < 8:
            return {
                'valid': False,
                'error': 'Password must be at least 8 characters long',
                'code': 'PASSWORD_TOO_SHORT'
            }
        
        if len(password) > 128:
            return {
                'valid': False,
                'error': 'Password is too long (max 128 characters)',
                'code': 'PASSWORD_TOO_LONG'
            }
        
        # Strength requirements
        requirements = []
        
        if not re.search(r'[A-Z]', password):
            requirements.append('one uppercase letter')
        
        if not re.search(r'[a-z]', password):
            requirements.append('one lowercase letter')
        
        if not re.search(r'\d', password):
            requirements.append('one number')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            requirements.append('one special character')
        
        if requirements:
            return {
                'valid': False,
                'error': f"Password must contain at least: {', '.join(requirements)}",
                'code': 'PASSWORD_WEAK'
            }
        
        # Check for common weak passwords
        weak_passwords = [
            'password', '12345678', 'qwerty123', 'abc12345',
            'password123', 'admin123', 'welcome123'
        ]
        
        if password.lower() in weak_passwords:
            return {
                'valid': False,
                'error': 'Password is too common and easily guessable',
                'code': 'PASSWORD_TOO_COMMON'
            }
        
        return {'valid': True}
    
    @staticmethod
    def validate_login_data(data: dict) -> Dict[str, Any]:
        """
        Validate login request data
        
        Args:
            data (dict): Login data to validate
            
        Returns:
            dict: Validation result
        """
        # Check required fields
        required_validation = RequestValidator.validate_required_fields(
            data, ['email', 'password']
        )
        
        if not required_validation['valid']:
            return required_validation
        
        errors = []
        
        # Validate email
        email_validation = RequestValidator.validate_email(data['email'])
        if not email_validation['valid']:
            errors.append({
                'field': 'email',
                'message': email_validation['error'],
                'code': email_validation['code']
            })
        
        # For login, we don't validate password strength (just presence)
        if not data.get('password'):
            errors.append({
                'field': 'password',
                'message': 'Password is required',
                'code': 'PASSWORD_REQUIRED'
            })
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    @staticmethod
    def validate_registration_data(data: dict) -> Dict[str, Any]:
        """
        Validate user registration data
        
        Args:
            data (dict): Registration data to validate
            
        Returns:
            dict: Validation result
        """
        # Check required fields
        required_validation = RequestValidator.validate_required_fields(
            data, ['username', 'email', 'password']
        )
        
        if not required_validation['valid']:
            return required_validation
        
        errors = []
        
        # Validate username
        username_validation = RequestValidator.validate_username(data['username'])
        if not username_validation['valid']:
            errors.append({
                'field': 'username',
                'message': username_validation['error'],
                'code': username_validation['code']
            })
        
        # Validate email
        email_validation = RequestValidator.validate_email(data['email'])
        if not email_validation['valid']:
            errors.append({
                'field': 'email',
                'message': email_validation['error'],
                'code': email_validation['code']
            })
        
        # Validate password
        password_validation = RequestValidator.validate_password(data['password'])
        if not password_validation['valid']:
            errors.append({
                'field': 'password',
                'message': password_validation['error'],
                'code': password_validation['code']
            })
        
        # Check password confirmation if provided
        if 'confirm_password' in data:
            if data['password'] != data['confirm_password']:
                errors.append({
                    'field': 'confirm_password',
                    'message': 'Password confirmation does not match',
                    'code': 'PASSWORD_MISMATCH'
                })
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    @staticmethod
    def sanitize_input(data: dict, allowed_fields: list = None) -> dict:
        """
        Sanitize input data by removing unwanted fields and trimming strings
        
        Args:
            data (dict): Data to sanitize
            allowed_fields (list): List of allowed fields (if None, all fields are kept)
            
        Returns:
            dict: Sanitized data
        """
        sanitized = {}
        
        for key, value in data.items():
            # Skip fields not in allowed list (if specified)
            if allowed_fields and key not in allowed_fields:
                continue
            
            # Trim string values
            if isinstance(value, str):
                sanitized[key] = value.strip()
            else:
                sanitized[key] = value
        
        return sanitized

# Decorator functions for request validation
def validate_json(required_fields: list = None):
    """
    Decorator to validate JSON request data
    
    Args:
        required_fields (list): List of required field names
        
    Returns:
        function: Decorated function
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if request has JSON data
            if not request.is_json:
                return jsonify({
                    'success': False,
                    'error': 'Request must be JSON',
                    'code': 'INVALID_CONTENT_TYPE'
                }), 400
            
            try:
                data = request.get_json()
            except Exception:
                return jsonify({
                    'success': False,
                    'error': 'Invalid JSON format',
                    'code': 'INVALID_JSON'
                }), 400
            
            # Validate required fields if specified
            if required_fields:
                validation_result = RequestValidator.validate_required_fields(
                    data, required_fields
                )
                
                if not validation_result['valid']:
                    return jsonify({
                        'success': False,
                        'error': 'Validation failed',
                        'errors': validation_result['errors'],
                        'code': 'VALIDATION_FAILED'
                    }), 400
            
            # Add validated data to kwargs
            kwargs['validated_data'] = data
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def validate_registration():
    """
    Decorator specifically for registration endpoint validation
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check JSON
            if not request.is_json:
                return jsonify({
                    'success': False,
                    'error': 'Request must be JSON',
                    'code': 'INVALID_CONTENT_TYPE'
                }), 400
            
            try:
                data = request.get_json()
            except Exception:
                return jsonify({
                    'success': False,
                    'error': 'Invalid JSON format',
                    'code': 'INVALID_JSON'
                }), 400
            
            # Validate registration data
            validation_result = RequestValidator.validate_registration_data(data)
            
            if not validation_result['valid']:
                return jsonify({
                    'success': False,
                    'error': 'Validation failed',
                    'errors': validation_result['errors'],
                    'code': 'VALIDATION_FAILED'
                }), 400
            
            # Sanitize input
            sanitized_data = RequestValidator.sanitize_input(
                data, ['username', 'email', 'password']
            )
            
            kwargs['validated_data'] = sanitized_data
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def validate_login():
    """
    Decorator specifically for login endpoint validation
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check JSON
            if not request.is_json:
                return jsonify({
                    'success': False,
                    'error': 'Request must be JSON',
                    'code': 'INVALID_CONTENT_TYPE'
                }), 400
            
            try:
                data = request.get_json()
            except Exception:
                return jsonify({
                    'success': False,
                    'error': 'Invalid JSON format',
                    'code': 'INVALID_JSON'
                }), 400
            
            # Validate login data
            validation_result = RequestValidator.validate_login_data(data)
            
            if not validation_result['valid']:
                return jsonify({
                    'success': False,
                    'error': 'Validation failed',
                    'errors': validation_result['errors'],
                    'code': 'VALIDATION_FAILED'
                }), 400
            
            # Sanitize input
            sanitized_data = RequestValidator.sanitize_input(
                data, ['email', 'password']
            )
            
            kwargs['validated_data'] = sanitized_data
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator