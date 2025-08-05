
from functools import wraps
from flask import request, current_app, jsonify
from app.models.user import User
from app.utils.validators import create_error_response
import jwt

def get_db():
    """Get database connection"""
    from pymongo import MongoClient
    client = MongoClient(current_app.config['MONGODB_URI'])
    return client[current_app.config['DATABASE_NAME']]

def verify_token(f):
    """Decorator to verify JWT tokens for protected routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # Check for token in Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                # Expected format: "Bearer TOKEN"
                token = auth_header.split(" ")[1]
            except IndexError:
                return create_error_response('Invalid authorization header format'), 401
        
        if not token:
            return create_error_response('Authentication token is missing'), 401
        
        try:
            # Decode the token
            payload = jwt.decode(
                token, 
                current_app.config['JWT_SECRET_KEY'], 
                algorithms=['HS256']
            )
            
            # Get user data from token
            current_user_id = payload['user_id']
            
            # Verify user still exists and is active
            db = get_db()
            user_model = User(db)
            current_user = user_model.find_by_id(current_user_id)
            
            if not current_user:
                return create_error_response('User not found'), 401
            
            if not current_user.get('is_active', True):
                return create_error_response('Account is deactivated'), 401
            
            # Add user data to request context
            request.current_user = current_user
            request.current_user_id = current_user_id
            
        except jwt.ExpiredSignatureError:
            return create_error_response('Token has expired'), 401
        except jwt.InvalidTokenError:
            return create_error_response('Invalid token'), 401
        except Exception as e:
            current_app.logger.error(f"Token verification error: {str(e)}")
            return create_error_response('Token verification failed'), 401
        
        return f(*args, **kwargs)
    
    return decorated_function

def admin_required(f):
    """Decorator for admin-only routes (requires verify_token first)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(request, 'current_user') or not request.current_user.get('is_admin', False):
            return create_error_response('Admin access required'), 403
        return f(*args, **kwargs)
    
    return decorated_function