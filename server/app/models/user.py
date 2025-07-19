from pymongo import MongoClient
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import re
import os
from dotenv import load_dotenv

load_dotenv()

class User:
    def __init__(self, db_connection=None):
        """Initialize User model with database connection"""
        if db_connection:
            self.db = db_connection
        else:
            # Create new connection if none provided
            client = MongoClient(os.getenv('MONGODB_URI'))
            self.db = client.get_database(os.getenv('DB_NAME', 'auth_app'))
        
        self.users_collection = self.db.users
        
        # Create indexes for better performance
        self.users_collection.create_index("email", unique=True)
        self.users_collection.create_index("username", unique=True)
    
    def create_user(self, username, email, password):
        """
        Create a new user with validation
        
        Args:
            username (str): Username for the user
            email (str): Email address
            password (str): Plain text password (will be hashed)
            
        Returns:
            dict: Result with success status and user data or error message
        """
        try:
            # Validate input types and convert to string if needed
            username = str(username) if username is not None else ""
            email = str(email) if email is not None else ""
            password = str(password) if password is not None else ""
            
            # Validate input
            validation_result = self.validate_user_input(username, email, password)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'error': validation_result['error'],
                    'field': validation_result.get('field')
                }
            
            # Check if user already exists
            existing_user = self.get_user_by_email(email)
            if existing_user:
                return {
                    'success': False,
                    'error': 'User with this email already exists',
                    'field': 'email'
                }
            
            existing_username = self.get_user_by_username(username)
            if existing_username:
                return {
                    'success': False,
                    'error': 'Username already taken',
                    'field': 'username'
                }
            
            # Hash password
            password_hash = generate_password_hash(password)
            
            # Create user document
            user_doc = {
                'username': username.lower().strip(),
                'email': email.lower().strip(),
                'password_hash': password_hash,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'is_active': True,
                'last_login': None
            }
            
            # Insert user into database
            result = self.users_collection.insert_one(user_doc)
            
            # Return success with user data (excluding password)
            user_data = {
                'id': str(result.inserted_id),
                'username': user_doc['username'],
                'email': user_doc['email'],
                'created_at': user_doc['created_at'],
                'is_active': user_doc['is_active']
            }
            
            return {
                'success': True,
                'user': user_data,
                'message': 'User created successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Database error: {str(e)}',
                'field': None
            }
    
    def get_user_by_email(self, email):
        """
        Retrieve user by email address
        
        Args:
            email (str): Email address to search for
            
        Returns:
            dict or None: User document if found, None otherwise
        """
        try:
            user = self.users_collection.find_one({'email': email.lower().strip()})
            if user:
                user['id'] = str(user['_id'])
                del user['_id']
            return user
        except Exception:
            return None
    
    def get_user_by_username(self, username):
        """
        Retrieve user by username
        
        Args:
            username (str): Username to search for
            
        Returns:
            dict or None: User document if found, None otherwise
        """
        try:
            user = self.users_collection.find_one({'username': username.lower().strip()})
            if user:
                user['id'] = str(user['_id'])
                del user['_id']
            return user
        except Exception:
            return None
    
    def get_user_by_id(self, user_id):
        """
        Retrieve user by ID
        
        Args:
            user_id (str): User ID to search for
            
        Returns:
            dict or None: User document if found, None otherwise
        """
        try:
            user = self.users_collection.find_one({'_id': ObjectId(user_id)})
            if user:
                user['id'] = str(user['_id'])
                del user['_id']
            return user
        except Exception:
            return None
    
    def verify_password(self, email, password):
        """
        Verify user password for login
        
        Args:
            email (str): Email address
            password (str): Plain text password to verify
            
        Returns:
            dict: Result with success status and user data or error message
        """
        try:
            user = self.get_user_by_email(email)
            if not user:
                return {
                    'success': False,
                    'error': 'Invalid email or password'
                }
            
            if not user['is_active']:
                return {
                    'success': False,
                    'error': 'Account is deactivated'
                }
            
            if check_password_hash(user['password_hash'], password):
                # Update last login
                self.update_last_login(user['id'])
                
                # Return user data without password
                user_data = {
                    'id': user['id'],
                    'username': user['username'],
                    'email': user['email'],
                    'created_at': user['created_at'],
                    'is_active': user['is_active']
                }
                
                return {
                    'success': True,
                    'user': user_data,
                    'message': 'Login successful'
                }
            else:
                return {
                    'success': False,
                    'error': 'Invalid email or password'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Database error: {str(e)}'
            }
    
    def update_last_login(self, user_id):
        """
        Update user's last login timestamp
        
        Args:
            user_id (str): User ID to update
        """
        try:
            self.users_collection.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': {'last_login': datetime.utcnow()}}
            )
        except Exception:
            pass  # Silent fail for last login update
    
    def validate_user_input(self, username, email, password):
        """
        Validate user input for registration
        
        Args:
            username (str): Username to validate
            email (str): Email to validate
            password (str): Password to validate
            
        Returns:
            dict: Validation result with valid status and error details
        """
        # Check for empty fields
        if not username or not username.strip():
            return {
                'valid': False,
                'error': 'Username is required',
                'field': 'username'
            }
        
        if not email or not email.strip():
            return {
                'valid': False,
                'error': 'Email is required',
                'field': 'email'
            }
        
        if not password:
            return {
                'valid': False,
                'error': 'Password is required',
                'field': 'password'
            }
        
        # Validate username
        username = username.strip()
        if len(username) < 3:
            return {
                'valid': False,
                'error': 'Username must be at least 3 characters long',
                'field': 'username'
            }
        
        if len(username) > 20:
            return {
                'valid': False,
                'error': 'Username must be less than 20 characters',
                'field': 'username'
            }
        
        # Username should only contain alphanumeric characters and underscores
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return {
                'valid': False,
                'error': 'Username can only contain letters, numbers, and underscores',
                'field': 'username'
            }
        
        # Validate email
        email = email.strip()
        if not self.is_valid_email(email):
            return {
                'valid': False,
                'error': 'Invalid email format',
                'field': 'email'
            }
        
        # Validate password
        password_validation = self.validate_password_strength(password)
        if not password_validation['valid']:
            return password_validation
        
        return {'valid': True}
    
    def is_valid_email(self, email):
        """
        Validate email format using regex
        
        Args:
            email (str): Email to validate
            
        Returns:
            bool: True if valid email format, False otherwise
        """
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_pattern, email) is not None
    
    def validate_password_strength(self, password):
        """
        Validate password strength
        
        Args:
            password (str): Password to validate
            
        Returns:
            dict: Validation result with valid status and error details
        """
        if len(password) < 8:
            return {
                'valid': False,
                'error': 'Password must be at least 8 characters long',
                'field': 'password'
            }
        
        if len(password) > 128:
            return {
                'valid': False,
                'error': 'Password is too long (max 128 characters)',
                'field': 'password'
            }
        
        # Check for at least one uppercase letter
        if not re.search(r'[A-Z]', password):
            return {
                'valid': False,
                'error': 'Password must contain at least one uppercase letter',
                'field': 'password'
            }
        
        # Check for at least one lowercase letter
        if not re.search(r'[a-z]', password):
            return {
                'valid': False,
                'error': 'Password must contain at least one lowercase letter',
                'field': 'password'
            }
        
        # Check for at least one digit
        if not re.search(r'\d', password):
            return {
                'valid': False,
                'error': 'Password must contain at least one number',
                'field': 'password'
            }
        
        # Check for at least one special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return {
                'valid': False,
                'error': 'Password must contain at least one special character',
                'field': 'password'
            }
        
        return {'valid': True}
    
    def update_user(self, user_id, update_data):
        """
        Update user information
        
        Args:
            user_id (str): User ID to update
            update_data (dict): Data to update
            
        Returns:
            dict: Result with success status and message
        """
        try:
            # Add updated_at timestamp
            update_data['updated_at'] = datetime.utcnow()
            
            result = self.users_collection.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': update_data}
            )
            
            if result.modified_count > 0:
                return {
                    'success': True,
                    'message': 'User updated successfully'
                }
            else:
                return {
                    'success': False,
                    'error': 'User not found or no changes made'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Database error: {str(e)}'
            }
    
    def deactivate_user(self, user_id):
        """
        Deactivate a user account
        
        Args:
            user_id (str): User ID to deactivate
            
        Returns:
            dict: Result with success status and message
        """
        return self.update_user(user_id, {'is_active': False})
    
    def activate_user(self, user_id):
        """
        Activate a user account
        
        Args:
            user_id (str): User ID to activate
            
        Returns:
            dict: Result with success status and message
        """
        return self.update_user(user_id, {'is_active': True})