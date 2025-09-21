"""
Synthesis Flask Application
A modern Flask application with MongoDB integration
"""

import os
import logging
from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from config import get_config, validate_config
from datetime import datetime
from app.routes.healthcare_gan_routes import healthcare_gan_bp

# Application metadata
__version__ = '1.0.0'
__author__ = 'Synthesis Team'

def create_app(config_name=None):
    """
    Application factory pattern
    Creates and configures a Flask application instance
    """
    
    # Create Flask app
    app = Flask(__name__)
    
    # Load configuration
    if config_name is None:
        config_name = os.environ.get('ENVIRONMENT', 'development')
    
    config_class = get_config()
    app.config.from_object(config_class)
    
    # Validate configuration
    try:
        validate_config()
    except ValueError as e:
        app.logger.error(f"Configuration error: {e}")
        raise
    
    # Initialize configuration
    config_class.init_app(app)
    
    # Initialize extensions
    init_extensions(app)
    
    # Initialize database connection
    init_database(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register middleware
    register_middleware(app)
    
    # Add custom CLI commands
    register_cli_commands(app)
    
    # Application context processors
    register_context_processors(app)
    
    app.register_blueprint(healthcare_gan_bp)

    return app

def init_extensions(app):
    """Initialize Flask extensions"""
    
    # Initialize CORS
    CORS(app, 
         origins=app.config['CORS_ORIGINS'],
         methods=app.config['CORS_METHODS'],
         allow_headers=app.config['CORS_ALLOW_HEADERS'],
         supports_credentials=True)
    
    app.logger.info("Extensions initialized")

def init_database(app):
    """Initialize database connection"""
    try:
        # Test MongoDB connection
        client = MongoClient(app.config['MONGODB_URI'], serverSelectionTimeoutMS=5000)
        # Force connection to test
        client.server_info()
        
        # Store client in app context for access in routes
        app.mongodb_client = client
        app.db = client[app.config['DATABASE_NAME']]
        
        app.logger.info(f"Connected to MongoDB: {app.config['DATABASE_NAME']}")
        
    except Exception as e:
        app.logger.error(f"Failed to connect to MongoDB: {e}")
        # In development, we might want to continue without DB
        if app.config.get('DEBUG'):
            app.logger.warning("Continuing without database connection in debug mode")
        else:
            raise

def register_blueprints(app):
    """Register application blueprints"""
    
    # Import and register blueprints
    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)
    
    # Register main routes
    @app.route('/')
    def index():
        return jsonify({
            'success': True,
            'message': 'Synthesis API Server',
            'version': __version__,
            'timestamp': datetime.utcnow().isoformat(),
            'endpoints': {
                'health': '/api/health',
                'auth': '/api/auth/',
                'docs': '/api/docs'
            }
        })
    
    @app.route('/api/health')
    def health_check():
        """Comprehensive health check endpoint"""
        health_status = {
            'success': True,
            'service': 'Synthesis API',
            'version': __version__,
            'timestamp': datetime.utcnow().isoformat(),
            'environment': app.config.get('ENVIRONMENT', 'development'),
            'database': 'connected',
            'status': 'healthy'
        }
        
        # Check database connection
        try:
            app.mongodb_client.server_info()
            health_status['database'] = 'connected'
        except:
            health_status['database'] = 'disconnected'
            health_status['status'] = 'unhealthy'
            health_status['success'] = False
        
        status_code = 200 if health_status['success'] else 503
        return jsonify(health_status), status_code
    
    app.logger.info("Blueprints registered")

def register_error_handlers(app):
    """Register application error handlers"""
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 'Bad Request',
            'message': 'The request could not be understood by the server',
            'status_code': 400
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'success': False,
            'error': 'Unauthorized',
            'message': 'Authentication required',
            'status_code': 401
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'success': False,
            'error': 'Forbidden',
            'message': 'Access denied',
            'status_code': 403
        }), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 'Not Found',
            'message': 'The requested resource was not found',
            'status_code': 404
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'success': False,
            'error': 'Method Not Allowed',
            'message': 'The method is not allowed for this resource',
            'status_code': 405
        }), 405
    
    @app.errorhandler(500)
    def internal_server_error(error):
        app.logger.error(f"Internal server error: {error}")
        return jsonify({
            'success': False,
            'error': 'Internal Server Error',
            'message': 'An internal server error occurred',
            'status_code': 500
        }), 500
    
    app.logger.info("Error handlers registered")

def register_middleware(app):
    """Register custom middleware"""
    
    @app.before_request
    def before_request():
        """Before request middleware"""
        # Log request info in debug mode
        if app.debug:
            app.logger.debug(f"Request: {request.method} {request.url}")
    
    @app.after_request
    def after_request(response):
        """After request middleware"""
        # Add security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Log response info in debug mode
        if app.debug:
            app.logger.debug(f"Response: {response.status_code}")
        
        return response
    
    app.logger.info("Middleware registered")

def register_cli_commands(app):
    """Register custom CLI commands"""
    
    @app.cli.command()
    def init_db():
        """Initialize database with default data"""
        try:
            db = app.db
            
            # Create indexes
            db.users.create_index("email", unique=True)
            db.users.create_index("created_at")
            
            print("Database initialized successfully!")
            
        except Exception as e:
            print(f"Error initializing database: {e}")
    
    @app.cli.command()
    def create_admin():
        """Create admin user"""
        from app.models.user import User
        
        email = input("Enter admin email: ")
        password = input("Enter admin password: ")
        
        try:
            user_model = User(app.db)
            
            if user_model.email_exists(email):
                print("Email already exists!")
                return
            
            admin_data = {
                'email': email,
                'password': password,
                'first_name': 'Admin',
                'last_name': 'User',
                'is_admin': True,
                'email_verified': True
            }
            
            user_id = user_model.create_user(admin_data)
            print(f"Admin user created with ID: {user_id}")
            
        except Exception as e:
            print(f"Error creating admin: {e}")

def register_context_processors(app):
    """Register template context processors"""
    
    @app.context_processor
    def utility_processor():
        """Add utility functions to template context"""
        return {
            'app_name': 'Synthesis',
            'app_version': __version__,
            'current_year': datetime.utcnow().year
        }

# Application instance for imports
app = None