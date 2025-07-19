from flask import Flask
from flask_cors import CORS
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager
from app.config import config
from flask_bcrypt import Bcrypt

mongo = PyMongo()
jwt = JWTManager()
bcrypt= Bcrypt()

def create_app(config_name=None):
    app= Flask(__name__)
    if config_name is None:
        config_name = app.config.get('FLASK_ENV','development')

    app.config.from_object(config[config_name])

    if not app.config.get('MONGO_URI'):
        raise ValueError("MONGO_URI must be set in the .env variables")
        
    mongo.init_app(app)
    jwt.init_app(app)   
    bcrypt.init_app(app)
    CORS(app,origins=app.config['CORS_ORIGINS'])

 # Register blueprints (commented out for now - will be added in later phases)
    # from app.routes.auth import auth_bp
    # from app.routes.user import user_bp
    # from app.routes.ml import ml_bp
    
    # app.register_blueprint(auth_bp, url_prefix='/auth')
    # app.register_blueprint(user_bp, url_prefix='/user')
    # app.register_blueprint(ml_bp, url_prefix='/ml')

# Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {"message": "Resource not found"}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return {'error': "Internal server error"}, 500   

    @app.errorhandler(400)
    def bad_request(error):
        return {"message": "Bad request"}, 400
    
# self health checkpoint
    @app.route('/health')
    def health_check():
        return {
            'status' : 'Healthy',
            'message': 'Server is running',
            'environement':app.config['FLASK_ENV']
        },200
    
    @app.route('/test-db')
    def test_db():
        try:
            mongo.db.command('ping')
            return{
                'status': 'Healthy',
                'message': 'Database connection is healthy',
                'database': mongo.db.name
            }
        
        except Exception as e:
            return {
                'status': 'Unhealthy',
                'message': f'Database connection failed: {str(e)}'
            }, 500
        
    return app