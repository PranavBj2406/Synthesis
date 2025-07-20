# app/middleware/auth.py
from functools import wraps
from flask import request, jsonify, current_app
import jwt
from app.models.user import User

def token_required(f):
    """
    Decorator to protect routes that require authentication.
    Validates JWT token and provides user info to the route.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check if token is provided in Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                # Expected format: "Bearer <token>"
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({
                    'success': False,
                    'message': 'Token format is invalid. Use: Bearer <token>'
                }), 401
        
        if not token:
            return jsonify({
                'success': False,
                'message': 'Token is missing. Please provide a valid token.'
            }), 401
        
        try:
            # Decode the JWT token
            data = jwt.decode(
                token, 
                current_app.config['SECRET_KEY'], 
                algorithms=['HS256']
            )
            
            # Get user from database using user_id from token
            current_user = User.find_by_id(data['user_id'])
            
            if not current_user:
                return jsonify({
                    'success': False,
                    'message': 'User not found. Token may be invalid.'
                }), 401
                
        except jwt.ExpiredSignatureError:
            return jsonify({
                'success': False,
                'message': 'Token has expired. Please login again.'
            }), 401
            
        except jwt.InvalidTokenError:
            return jsonify({
                'success': False,
                'message': 'Token is invalid. Please provide a valid token.'
            }), 401
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': 'Token validation failed.',
                'error': str(e)
            }), 401
        
        # Pass current_user to the route function
        return f(current_user, *args, **kwargs)
    
    return decorated


def optional_token(f):
    """
    Decorator for routes where authentication is optional.
    If token is provided, user info is passed; otherwise, user is None.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        current_user = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
                
                # Try to decode the token
                data = jwt.decode(
                    token, 
                    current_app.config['SECRET_KEY'], 
                    algorithms=['HS256']
                )
                
                # Get user from database
                current_user = User.find_by_id(data['user_id'])
                
            except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, IndexError):
                # If token is invalid, just continue with current_user as None
                pass
        
        return f(current_user, *args, **kwargs)
    
    return decorated


def admin_required(f):
    """
    Decorator for routes that require admin privileges.
    First validates token, then checks if user has admin role.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # First check if user is authenticated
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({
                    'success': False,
                    'message': 'Token format is invalid. Use: Bearer <token>'
                }), 401
        
        if not token:
            return jsonify({
                'success': False,
                'message': 'Admin access requires authentication token.'
            }), 401
        
        try:
            # Decode the JWT token
            data = jwt.decode(
                token, 
                current_app.config['SECRET_KEY'], 
                algorithms=['HS256']
            )
            
            # Get user from database
            current_user = User.find_by_id(data['user_id'])
            
            if not current_user:
                return jsonify({
                    'success': False,
                    'message': 'User not found.'
                }), 401
            
            # Check if user has admin role
            if not current_user.get('is_admin', False):
                return jsonify({
                    'success': False,
                    'message': 'Admin privileges required for this action.'
                }), 403
                
        except jwt.ExpiredSignatureError:
            return jsonify({
                'success': False,
                'message': 'Token has expired. Please login again.'
            }), 401
            
        except jwt.InvalidTokenError:
            return jsonify({
                'success': False,
                'message': 'Token is invalid.'
            }), 401
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': 'Authentication failed.',
                'error': str(e)
            }), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated


def get_current_user_from_token():
    """
    Utility function to get current user from token without using decorator.
    Returns user object if valid token, None otherwise.
    """
    if 'Authorization' not in request.headers:
        return None
    
    try:
        auth_header = request.headers['Authorization']
        token = auth_header.split(" ")[1]
        
        data = jwt.decode(
            token, 
            current_app.config['SECRET_KEY'], 
            algorithms=['HS256']
        )
        
        return User.find_by_id(data['user_id'])
        
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, IndexError):
        return None