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
from app.utils.auth_decorators import verify_token
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
            return create_validation_error_response(errors), 400
        
        # Initialize database and user model
        db = get_db()
        user_model = User(db)
        
        # Check if user already exists (email or username)
        if user_model.email_exists(data['email']):
            return create_error_response('Email already registered', 'email'), 409
        
        if user_model.username_exists(data['username']):
            return create_error_response('Username already taken', 'username'), 409
        
        # Prepare user data - UPDATED schema
        user_data = {
            'username': data['username'],
            'email': data['email'],
            'password': data['password'],
            'phone': data.get('phone', ''),  # Optional field
            # Remove other optional fields or add as needed
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
            'username': data['username'],
            'exp': datetime.utcnow() + timedelta(days=7)  # Token expires in 7 days
        }
        
        token = jwt.encode(
            token_payload, 
            current_app.config['JWT_SECRET_KEY'], 
            algorithm='HS256'
        )
        
        # Success response - UPDATED response structure
        return jsonify({
            'success': True,
            'message': 'Account created successfully',
            'data': {
                'user_id': user_id,
                'email': data['email'],
                'username': data['username'],
                'phone': data.get('phone', ''),
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

@auth_bp.route('/check-username', methods=['POST'])
def check_username():
    """Check if username already exists"""
    try:
        data = request.get_json()
        
        if not data or 'username' not in data:
            return create_error_response('Username is required'), 400
        
        username = data['username'].strip().lower()
        
        # Validate username format
        from app.utils.validators import validate_username
        if not validate_username(username):
            return create_error_response('Invalid username format', 'username'), 400
        
        # Check database
        db = get_db()
        user_model = User(db)
        
        exists = user_model.username_exists(username)
        
        return jsonify({
            'success': True,
            'exists': exists,
            'message': 'Username already taken' if exists else 'Username available'
        })
        
    except Exception as e:
        current_app.logger.error(f"Username check error: {str(e)}")
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

@auth_bp.route('/signin', methods=['POST'])
def signin():
    """User signin endpoint"""
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            return create_error_response('No data provided'), 400
        
        # Sanitize input data
        data = sanitize_input(data)
        
        # Validate required fields
        if not data.get('login') or not data.get('password'):
            return create_error_response('Login and password are required'), 400
        
        login = data['login'].strip().lower()
        password = data['password']
        
        # Initialize database and user model
        db = get_db()
        user_model = User(db)
        
        # Find user by email or username
        user = None
        if '@' in login:
            # Login with email
            user = user_model.find_by_email(login)
        else:
            # Login with username
            user = user_model.find_by_username(login)
        
        # Check if user exists
        if not user:
            return create_error_response('Invalid login credentials'), 401
        
        # Check if account is active
        if not user.get('is_active', True):
            return create_error_response('Account is deactivated'), 401
        
        # Verify password
        if not user_model.verify_password(user, password):
            return create_error_response('Invalid login credentials'), 401
        
        # Generate JWT token
        token_payload = {
            'user_id': str(user['_id']),
            'email': user['email'],
            'username': user['username'],
            'exp': datetime.utcnow() + timedelta(days=7)  # Token expires in 7 days
        }
        
        token = jwt.encode(
            token_payload, 
            current_app.config['JWT_SECRET_KEY'], 
            algorithm='HS256'
        )
        
        # Success response - matching your signup response structure
        response_data = {
            'user_id': str(user['_id']),
            'email': user['email'],
            'username': user['username'],
            'token': token
        }
        
        # Include phone if available
        if user.get('phone'):
            response_data['phone'] = user['phone']
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'data': response_data
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Signin error: {str(e)}")
        return create_error_response('Internal server error'), 500

# ADD: Protected routes using the decorator
@auth_bp.route('/profile', methods=['GET'])
@verify_token
def get_profile():
    """Get user profile - requires authentication"""
    try:
        user = request.current_user
        
        # Return user profile data (excluding sensitive information)
        profile_data = {
            'user_id': str(user['_id']),
            'email': user['email'],
            'username': user['username'],
            'phone': user.get('phone', ''),
            'date_of_birth': user.get('date_of_birth', ''),
            'gender': user.get('gender', ''),
            'profile_picture': user.get('profile_picture', ''),
            'created_at': user.get('created_at').isoformat() if user.get('created_at') else None,
            'email_verified': user.get('email_verified', False)
        }
        
        return jsonify({
            'success': True,
            'message': 'Profile retrieved successfully',
            'data': profile_data
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Profile retrieval error: {str(e)}")
        return create_error_response('Failed to retrieve profile'), 500

@auth_bp.route('/profile', methods=['PUT'])
@verify_token
def update_profile():
    """Update user profile - requires authentication"""
    try:
        data = request.get_json()
        user_id = request.current_user_id
        
        if not data:
            return create_error_response('No data provided'), 400
        
        # Sanitize input data
        data = sanitize_input(data)
        
        # Define allowed fields for profile update
        allowed_fields = ['phone', 'date_of_birth', 'gender', 'profile_picture']
        update_data = {k: v for k, v in data.items() if k in allowed_fields}
        
        if not update_data:
            return create_error_response('No valid fields to update'), 400
        
        # Update user
        db = get_db()
        user_model = User(db)
        
        if user_model.update_user(user_id, update_data):
            return jsonify({
                'success': True,
                'message': 'Profile updated successfully'
            }), 200
        else:
            return create_error_response('Failed to update profile'), 500
        
    except Exception as e:
        current_app.logger.error(f"Profile update error: {str(e)}")
        return create_error_response('Failed to update profile'), 500

@auth_bp.route('/logout', methods=['POST'])
@verify_token
def logout():
    """User logout endpoint"""
    try:
        # In a stateless JWT system, logout is mainly handled on the client side
        # by removing the token. However, you can add token blacklisting here if needed.
        
        return jsonify({
            'success': True,
            'message': 'Logged out successfully'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Logout error: {str(e)}")
        return create_error_response('Logout failed'), 500

# ADD: Password reset functionality
@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Request password reset"""
    try:
        data = request.get_json()
        
        if not data or not data.get('email'):
            return create_error_response('Email is required'), 400
        
        email = data['email'].strip().lower()
        
        # Validate email format
        from app.utils.validators import validate_email_format
        if not validate_email_format(email):
            return create_error_response('Invalid email format'), 400
        
        # Check if user exists
        db = get_db()
        user_model = User(db)
        user = user_model.find_by_email(email)
        
        if not user:
            # For security, return success even if email doesn't exist
            return jsonify({
                'success': True,
                'message': 'If the email exists, a password reset link has been sent'
            }), 200
        
        # Generate password reset token (shorter expiry)
        reset_payload = {
            'user_id': str(user['_id']),
            'email': user['email'],
            'type': 'password_reset',
            'exp': datetime.utcnow() + timedelta(hours=1)  # 1 hour expiry
        }
        
        reset_token = jwt.encode(
            reset_payload, 
            current_app.config['JWT_SECRET_KEY'], 
            algorithm='HS256'
        )
        
        # TODO: Send email with reset link
        # For now, log the token (in production, send via email)
        current_app.logger.info(f"Password reset token for {email}: {reset_token}")
        
        return jsonify({
            'success': True,
            'message': 'If the email exists, a password reset link has been sent'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Forgot password error: {str(e)}")
        return create_error_response('Failed to process password reset request'), 500
