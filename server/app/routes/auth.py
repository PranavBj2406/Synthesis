from flask import Blueprint, request, jsonify, current_app
from pymongo import MongoClient
from app.models.user import User
from app.utils.validators import (
    validate_signup_data, 
    sanitize_input,
    create_error_response,
    create_validation_error_response
)
import jwt
from datetime import datetime, timedelta
import os

# Create Blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# Initialize MongoDB connection
def get_db():
    """Get database connection"""
    client = MongoClient(current_app.config['MONGODB_URI'])
    return client[current_app.config['DATABASE_NAME']]

@auth_bp.route('/signup', methods=['POST'])
def signup():
    """User signup endpoint"""
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            return create_error_response('No data provided'), 400
        
        # Sanitize input data
        data = sanitize_input(data)
        
        # Validate input data
        is_valid, errors = validate_signup_data(data)
        if not is_valid:
            return create_validation_error_response(errors)
        
        # Initialize database and user model
        db = get_db()
        user_model = User(db)
        
        # Check if user already exists
        if user_model.email_exists(data['email']):
            return create_error_response('Email already registered', 'email'), 409
        
        # Prepare user data
        user_data = {
            'email': data['email'],
            'password': data['password'],
            'first_name': data['first_name'],
            'last_name': data['last_name'],
            'phone': data.get('phone', ''),
            'date_of_birth': data.get('date_of_birth', ''),
            'gender': data.get('gender', ''),
            'profile_picture': data.get('profile_picture', ''),
        }
        
        # Create user
        user_id = user_model.create_user(user_data)
        
        # Generate JWT token for immediate login (optional)
        token_payload = {
            'user_id': user_id,
            'email': data['email'],
            'exp': datetime.utcnow() + timedelta(days=7)  # Token expires in 7 days
        }
        
        token = jwt.encode(
            token_payload, 
            current_app.config['JWT_SECRET_KEY'], 
            algorithm='HS256'
        )
        
        # Success response
        return jsonify({
            'success': True,
            'message': 'Account created successfully',
            'data': {
                'user_id': user_id,
                'email': data['email'],
                'first_name': data['first_name'],
                'last_name': data['last_name'],
                'token': token
            }
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Signup error: {str(e)}")
        return create_error_response('Internal server error'), 500

@auth_bp.route('/check-email', methods=['POST'])
def check_email():
    """Check if email already exists"""
    try:
        data = request.get_json()
        
        if not data or 'email' not in data:
            return create_error_response('Email is required'), 400
        
        email = data['email'].strip().lower()
        
        # Validate email format
        from app.utils.validators import validate_email_format
        if not validate_email_format(email):
            return create_error_response('Invalid email format', 'email'), 400
        
        # Check database
        db = get_db()
        user_model = User(db)
        
        exists = user_model.email_exists(email)
        
        return jsonify({
            'success': True,
            'exists': exists,
            'message': 'Email already registered' if exists else 'Email available'
        })
        
    except Exception as e:
        current_app.logger.error(f"Email check error: {str(e)}")
        return create_error_response('Internal server error'), 500

@auth_bp.route('/validate-password', methods=['POST'])
def validate_password():
    """Validate password strength"""
    try:
        data = request.get_json()
        
        if not data or 'password' not in data:
            return create_error_response('Password is required'), 400
        
        from app.utils.validators import validate_password_strength
        is_valid, message = validate_password_strength(data['password'])
        
        return jsonify({
            'success': True,
            'valid': is_valid,
            'message': message
        })
        
    except Exception as e:
        current_app.logger.error(f"Password validation error: {str(e)}")
        return create_error_response('Internal server error'), 500

# Health check endpoint
@auth_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'message': 'Auth service is running',
        'timestamp': datetime.utcnow().isoformat()
    })

# Error handlers for this blueprint
@auth_bp.errorhandler(400)
def bad_request(error):
    return create_error_response('Bad request'), 400

@auth_bp.errorhandler(404)
def not_found(error):
    return create_error_response('Endpoint not found'), 404

@auth_bp.errorhandler(500)
def internal_error(error):
    return create_error_response('Internal server error'), 500