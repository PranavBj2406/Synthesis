from flask import jsonify
import re

class ValidationError(Exception):
    """Custom validation error"""
    def __init__(self, message, field=None):
        self.message = message
        self.field = field
        super().__init__(self.message)

def validate_signup_data(data):
    """
    Validate signup form data
    Returns: tuple (is_valid, errors)
    """
    errors = {}
    
    # Check required fields - UPDATED to use username instead of first_name/last_name  
    required_fields = ['email', 'password','username']
    for field in required_fields:
        if field not in data or not data[field].strip():
            errors[field] = f"{field.replace('_', ' ').title()} is required"
    
    # Validate email
    if 'email' in data and data['email']:
        email = data['email'].strip().lower()
        if not validate_email_format(email):
            errors['email'] = "Please provide a valid email address"
    
    # Validate username
    if 'username' in data and data['username']:
        if not validate_username(data['username']):
            errors['username'] = "Username must be 3-20 characters long and contain only letters, numbers, and underscores"
    
    # Validate password
    if 'password' in data and data['password']:
        is_valid, message = validate_password_strength(data['password'])
        if not is_valid:
            errors['password'] = message
    

    
    # Validate phone if provided (OPTIONAL - only validate if present)
    if 'phone' in data and data['phone'] and data['phone'].strip():
        if not validate_phone(data['phone']):
            errors['phone'] = "Please provide a valid phone number"
    
    return len(errors) == 0, errors

def validate_email_format(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_username(username):
    """Validate username format"""
    # Username should be 3-20 characters, alphanumeric + underscores only
    if len(username.strip()) < 3 or len(username.strip()) > 20:
        return False
    return re.match(r'^[a-zA-Z0-9_]+$', username.strip()) is not None

def validate_password_strength(password):
    """
    Validate password strength
    Returns: tuple (is_valid, message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    
    return True, "Password is valid"

def validate_phone(phone):
    """Validate phone number format"""
    # Remove all non-digit characters
    clean_phone = re.sub(r'\D', '', phone)
    # Check if it's 10 digits long (adjust as needed for your region)
    return len(clean_phone) == 10

def sanitize_input(data):
    """Sanitize input data"""
    sanitized = {}
    for key, value in data.items():
        if isinstance(value, str):
            # Strip whitespace and convert email to lowercase
            if key == 'email':
                sanitized[key] = value.strip().lower()
            elif key == 'username':
                sanitized[key] = value.strip().lower()  # Username to lowercase
            else:
                sanitized[key] = value.strip()
        else:
            sanitized[key] = value
    return sanitized

def create_error_response(message, field=None):
    """Create standardized error response"""
    response = {
        'success': False,
        'message': message
    }
    if field:
        response['field'] = field
    
    return jsonify(response)

def create_validation_error_response(errors):
    """Create response for validation errors"""
    return jsonify({
        'success': False,
        'message': 'Validation failed',
        'errors': errors
    })