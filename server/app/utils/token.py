import jwt
import os
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
from dotenv import load_dotenv

load_dotenv()

class TokenManager:
    """JWT Token management utility class"""
    
    def __init__(self):
        # Get JWT configuration from environment
        self.secret_key = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-this-in-production')
        self.algorithm = 'HS256'
        
        # Token expiration times (in minutes)
        self.access_token_expiry = int(os.getenv('ACCESS_TOKEN_EXPIRY_MINUTES', 15))  # 15 minutes
        self.refresh_token_expiry = int(os.getenv('REFRESH_TOKEN_EXPIRY_DAYS', 7))    # 7 days
        
        # Issuer information
        self.issuer = os.getenv('JWT_ISSUER', 'auth_app')
    
    def generate_access_token(self, user_data):
        """
        Generate JWT access token for authenticated user
        
        Args:
            user_data (dict): User information to include in token
            
        Returns:
            str: JWT access token
        """
        try:
            # Token payload
            payload = {
                'user_id': user_data['id'],
                'username': user_data['username'],
                'email': user_data['email'],
                'iat': datetime.utcnow(),  # Issued at
                'exp': datetime.utcnow() + timedelta(minutes=self.access_token_expiry),  # Expiration
                'iss': self.issuer,  # Issuer
                'type': 'access'  # Token type
            }
            
            # Generate token
            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            return token
            
        except Exception as e:
            raise Exception(f"Error generating access token: {str(e)}")
    
    def generate_refresh_token(self, user_data):
        """
        Generate JWT refresh token for token renewal
        
        Args:
            user_data (dict): User information to include in token
            
        Returns:
            str: JWT refresh token
        """
        try:
            # Token payload (minimal data for refresh token)
            payload = {
                'user_id': user_data['id'],
                'username': user_data['username'],
                'iat': datetime.utcnow(),  # Issued at
                'exp': datetime.utcnow() + timedelta(days=self.refresh_token_expiry),  # Expiration
                'iss': self.issuer,  # Issuer
                'type': 'refresh'  # Token type
            }
            
            # Generate token
            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            return token
            
        except Exception as e:
            raise Exception(f"Error generating refresh token: {str(e)}")
    
    def verify_token(self, token, token_type='access'):
        """
        Verify and decode JWT token
        
        Args:
            token (str): JWT token to verify
            token_type (str): Expected token type ('access' or 'refresh')
            
        Returns:
            dict: Decoded token payload or None if invalid
        """
        try:
            # Decode token
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                issuer=self.issuer
            )
            
            # Verify token type
            if payload.get('type') != token_type:
                return {
                    'valid': False,
                    'error': f'Invalid token type. Expected {token_type}',
                    'code': 'INVALID_TOKEN_TYPE'
                }
            
            # Check if token is expired (JWT library handles this, but we can add custom logic)
            current_time = datetime.utcnow()
            exp_time = datetime.fromtimestamp(payload['exp'])
            
            if current_time > exp_time:
                return {
                    'valid': False,
                    'error': 'Token has expired',
                    'code': 'TOKEN_EXPIRED'
                }
            
            return {
                'valid': True,
                'payload': payload
            }
            
        except jwt.ExpiredSignatureError:
            return {
                'valid': False,
                'error': 'Token has expired',
                'code': 'TOKEN_EXPIRED'
            }
        except jwt.InvalidTokenError:
            return {
                'valid': False,
                'error': 'Invalid token',
                'code': 'INVALID_TOKEN'
            }
        except jwt.InvalidIssuerError:
            return {
                'valid': False,
                'error': 'Invalid token issuer',
                'code': 'INVALID_ISSUER'
            }
        except Exception as e:
            return {
                'valid': False,
                'error': f'Token verification error: {str(e)}',
                'code': 'VERIFICATION_ERROR'
            }
    
    def refresh_access_token(self, refresh_token):
        """
        Generate new access token using refresh token
        
        Args:
            refresh_token (str): Valid refresh token
            
        Returns:
            dict: Result with new access token or error
        """
        try:
            # Verify refresh token
            verification_result = self.verify_token(refresh_token, 'refresh')
            
            if not verification_result['valid']:
                return {
                    'success': False,
                    'error': verification_result['error'],
                    'code': verification_result['code']
                }
            
            # Extract user data from refresh token
            payload = verification_result['payload']
            user_data = {
                'id': payload['user_id'],
                'username': payload['username'],
                'email': payload.get('email', '')  # Email might not be in refresh token
            }
            
            # Generate new access token
            new_access_token = self.generate_access_token(user_data)
            
            return {
                'success': True,
                'access_token': new_access_token,
                'expires_in': self.access_token_expiry * 60  # Convert to seconds
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error refreshing token: {str(e)}',
                'code': 'REFRESH_ERROR'
            }
    
    def extract_token_from_header(self, auth_header):
        """
        Extract JWT token from Authorization header
        
        Args:
            auth_header (str): Authorization header value
            
        Returns:
            str or None: Extracted token or None if invalid format
        """
        if not auth_header:
            return None
        
        # Expected format: "Bearer <token>"
        parts = auth_header.split()
        
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return None
        
        return parts[1]
    
    def get_token_info(self, token):
        """
        Get information about a token without full verification
        (useful for debugging)
        
        Args:
            token (str): JWT token
            
        Returns:
            dict: Token information or None if invalid
        """
        try:
            # Decode without verification (for inspection only)
            payload = jwt.decode(token, options={"verify_signature": False})
            
            # Convert timestamps to readable format
            iat = datetime.fromtimestamp(payload['iat']) if 'iat' in payload else None
            exp = datetime.fromtimestamp(payload['exp']) if 'exp' in payload else None
            
            return {
                'user_id': payload.get('user_id'),
                'username': payload.get('username'),
                'email': payload.get('email'),
                'token_type': payload.get('type'),
                'issued_at': iat.isoformat() if iat else None,
                'expires_at': exp.isoformat() if exp else None,
                'issuer': payload.get('iss'),
                'is_expired': datetime.utcnow() > exp if exp else None
            }
            
        except Exception as e:
            return {
                'error': f'Cannot decode token: {str(e)}'
            }
    
    def invalidate_token(self, token):
        """
        Add token to blacklist (for logout functionality)
        Note: This requires a blacklist storage mechanism (Redis, database, etc.)
        For now, this is a placeholder that can be implemented based on your needs
        
        Args:
            token (str): Token to invalidate
            
        Returns:
            bool: True if successful
        """
        # TODO: Implement token blacklisting
        # This could store token JTI (JWT ID) in Redis or database
        # with expiration time matching the token's expiration
        
        try:
            # Get token info
            verification_result = self.verify_token(token)
            if verification_result['valid']:
                payload = verification_result['payload']
                # Here you would add the token to blacklist
                # For example: redis.setex(f"blacklist:{payload['jti']}", ttl, "true")
                return True
            return False
        except Exception:
            return False
    
    def is_token_blacklisted(self, token):
        """
        Check if token is blacklisted
        Note: This requires a blacklist storage mechanism
        
        Args:
            token (str): Token to check
            
        Returns:
            bool: True if blacklisted
        """
        # TODO: Implement blacklist checking
        # For example: return redis.exists(f"blacklist:{jti}")
        return False

# Global token manager instance
token_manager = TokenManager()

def generate_tokens(user_data):
    """
    Generate both access and refresh tokens for a user
    
    Args:
        user_data (dict): User information
        
    Returns:
        dict: Both tokens with expiration info
    """
    try:
        access_token = token_manager.generate_access_token(user_data)
        refresh_token = token_manager.generate_refresh_token(user_data)
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'access_token_expires_in': token_manager.access_token_expiry * 60,  # seconds
            'refresh_token_expires_in': token_manager.refresh_token_expiry * 24 * 60 * 60,  # seconds
            'token_type': 'Bearer'
        }
        
    except Exception as e:
        raise Exception(f"Error generating tokens: {str(e)}")

def verify_access_token(token):
    """
    Verify access token and return user data
    
    Args:
        token (str): Access token to verify
        
    Returns:
        dict: Verification result with user data
    """
    return token_manager.verify_token(token, 'access')

def verify_refresh_token(token):
    """
    Verify refresh token
    
    Args:
        token (str): Refresh token to verify
        
    Returns:
        dict: Verification result
    """
    return token_manager.verify_token(token, 'refresh')

def refresh_tokens(refresh_token):
    """
    Generate new access token using refresh token
    
    Args:
        refresh_token (str): Valid refresh token
        
    Returns:
        dict: New access token or error
    """
    return token_manager.refresh_access_token(refresh_token)