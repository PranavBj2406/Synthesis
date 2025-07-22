import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration class"""
    
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'dev-jwt-secret-key-change-in-production'
    
    # JWT Configuration
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_ALGORITHM = 'HS256'
    
    # MongoDB Configuration
    MONGODB_URI = os.environ.get('MONGODB_URI') or 'mongodb://localhost:27017/'
    DATABASE_NAME = os.environ.get('DATABASE_NAME') or 'synthesis_db'
    
    # Server Configuration
    HOST = os.environ.get('HOST') or '127.0.0.1'
    PORT = int(os.environ.get('PORT') or 5000)
    
    # CORS Configuration
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    CORS_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
    CORS_ALLOW_HEADERS = ['Content-Type', 'Authorization']
    
    # Email Configuration (for future email verification)
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'False').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or MAIL_USERNAME
    
    # File Upload Configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}
    
    # Rate Limiting Configuration
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL') or 'memory://'
    RATELIMIT_DEFAULT = "100 per hour"
    
    # Logging Configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    LOG_FILE = os.environ.get('LOG_FILE') or 'app.log'
    
    # Application Configuration
    TIMEZONE = os.environ.get('TIMEZONE') or 'UTC'
    PAGINATION_PER_PAGE = int(os.environ.get('PAGINATION_PER_PAGE') or 20)
    
    @staticmethod
    def init_app(app):
        """Initialize application with this configuration"""
        pass

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False
    
    # Development specific settings
    WTF_CSRF_ENABLED = False
    
    # Logging for development
    LOG_LEVEL = 'DEBUG'
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Development specific initialization
        import logging
        logging.basicConfig(level=logging.DEBUG)

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
    # Production security settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # HTTPS enforcement
    PREFERRED_URL_SCHEME = 'https'
    
    # Logging for production
    LOG_LEVEL = 'WARNING'
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Production specific initialization
        import logging
        from logging.handlers import RotatingFileHandler
        
        if not app.debug:
            # File logging
            file_handler = RotatingFileHandler(
                cls.LOG_FILE, 
                maxBytes=10240000, 
                backupCount=10
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
            
            app.logger.setLevel(logging.INFO)
            app.logger.info('Synthesis startup')

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    
    # Use in-memory database for testing
    DATABASE_NAME = 'synthesis_test_db'
    
    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False
    
    # JWT settings for testing
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Get configuration based on environment"""
    env = os.environ.get('ENVIRONMENT', 'development').lower()
    return config.get(env, config['default'])

def validate_config():
    """Validate required configuration variables"""
    required_vars = [
        'MONGODB_URI',
        'SECRET_KEY',
        'JWT_SECRET_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    return True