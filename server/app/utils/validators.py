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
    
    # Check required fields
    required_fields = ['email', 'password', 'first_name', 'last_name']
    for field in required_fields:
        if field not in data or not data[field].strip():
            errors[field] = f"{field.replace('_', ' ').title()} is required"
    
    # Validate email
    if 'email' in data and data['email']:
        email = data['email'].strip().lower()
        if not validate_email_format(email):
            errors['email'] = "Please provide a valid email address"
    
    # Validate password
    if 'password' in data and data['password']:
        is_valid, message = validate_password_strength(data['password'])
        if not is_valid:
            errors['password'] = message
    
    # Validate password confirmation
    if 'confirm_password' in data:
        if data.get('password') != data.get('confirm_password'):
            errors['confirm_password'] = "Passwords do not match"
    
    # Validate names
    if 'first_name' in data and data['first_name']:
        if not validate_name(data['first_name']):
            errors['first_name'] = "First name should only contain letters and spaces"
    
    if 'last_name' in data and data['last_name']:
        if not validate_name(data['last_name']):
            errors['last_name'] = "Last name should only contain letters and spaces"
    
    # Validate phone if provided
    if 'phone' in data and data['phone']:
        if not validate_phone(data['phone']):
            errors['phone'] = "Please provide a valid phone number"
    
    return len(errors) == 0, errors

def validate_email_format(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

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

def validate_name(name):
    """Validate name format - only letters and spaces"""
    return re.match(r'^[a-zA-Z\s]+$', name.strip()) is not None

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
            else:
                sanitized[key] = value.strip()
        else:
            sanitized[key] = value
    return sanitized

def create_error_response(message, field=None, status_code=400):
    """Create standardized error response"""
    response = {
        'success': False,
        'message': message
    }
    if field:
        response['field'] = field
    
    return jsonify(response), status_code

def create_validation_error_response(errors, status_code=400):
    """Create response for validation errors"""
    return jsonify({
        'success': False,
        'message': 'Validation failed',
        'errors': errors
    }), status_code