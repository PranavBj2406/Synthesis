from datetime import datetime
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
import re

class User:
    def __init__(self, db):
        self.collection = db.users
    
    def create_user(self, user_data):
        """Create a new user in the database"""
        # Hash the password
        user_data['password'] = generate_password_hash(user_data['password'])
        
        # Add metadata
        user_data['created_at'] = datetime.utcnow()
        user_data['updated_at'] = datetime.utcnow()
        user_data['is_active'] = True
        user_data['email_verified'] = False
        
        # Insert user and return the ID
        result = self.collection.insert_one(user_data)
        return str(result.inserted_id)
    
    def find_by_email(self, email):
        """Find user by email"""
        return self.collection.find_one({'email': email.lower()})
    
    def find_by_id(self, user_id):
        """Find user by ID"""
        try:
            return self.collection.find_one({'_id': ObjectId(user_id)})
        except:
            return None
    
    def email_exists(self, email):
        """Check if email already exists"""
        return self.collection.find_one({'email': email.lower()}) is not None
    
    def verify_password(self, user, password):
        """Verify user password"""
        return check_password_hash(user['password'], password)
    
    def update_user(self, user_id, update_data):
        """Update user information"""
        update_data['updated_at'] = datetime.utcnow()
        try:
            result = self.collection.update_one(
                {'_id': ObjectId(user_id)}, 
                {'$set': update_data}
            )
            return result.modified_count > 0
        except:
            return False
    
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_password(password):
        """
        Validate password strength
        At least 8 characters, 1 uppercase, 1 lowercase, 1 number
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        if not re.search(r'\d', password):
            return False, "Password must contain at least one number"
        
        return True, "Password is valid"