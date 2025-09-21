from flask import Blueprint, request, jsonify, current_app
import uuid
import logging

# Import the client
try:
    from app.ml.client import HealthcareGANClient
except ImportError:
    # Alternative import if above doesn't work
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from ml.client import HealthcareGANClient

logger = logging.getLogger(__name__)

# Create Healthcare GAN blueprint
healthcare_gan_bp = Blueprint('healthcare_gan', __name__, url_prefix='/api/healthcare-gan')

# Create client instance
gan_client = HealthcareGANClient()

@healthcare_gan_bp.route('/health', methods=['GET'])
def health_check():
    """Check Healthcare GAN service health"""
    try:
        result = gan_client.health_check()
        status_code = 200 if result["status"] == "healthy" else 503
        return jsonify(result), status_code
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({"status": "error", "error": str(e)}), 500

@healthcare_gan_bp.route('/metrics', methods=['GET'])
def get_metrics():
    """Get Healthcare GAN metrics"""
    try:
        result = gan_client.get_metrics()
        status_code = 200 if result["success"] else 500
        return jsonify(result), status_code
    except Exception as e:
        logger.error(f"Get metrics error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@healthcare_gan_bp.route('/train', methods=['POST'])
def train_models():
    """Train Healthcare GAN models"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"success": False, "error": "No training data provided"}), 400
        
        # Add request metadata
        if 'request_id' not in data:
            data['request_id'] = str(uuid.uuid4())
        
        # Call training endpoint
        result = gan_client.train_models(data)
        status_code = 200 if result["success"] else 500
        
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Training error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@healthcare_gan_bp.route('/generate', methods=['POST'])
def generate_data():
    """Generate synthetic healthcare data"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"success": False, "error": "No generation parameters provided"}), 400
        
        # Add request metadata
        if 'request_id' not in data:
            data['request_id'] = str(uuid.uuid4())
        
        # Call generation endpoint
        result = gan_client.generate_data(data)
        status_code = 200 if result["success"] else 500
        
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Generation error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@healthcare_gan_bp.route('/status', methods=['GET'])
def service_status():
    """Get overall service status"""
    try:
        health = gan_client.health_check()
        
        return jsonify({
            "service": "Healthcare GAN API Integration",
            "version": "1.0.0",
            "ml_service_health": health["status"],
            "endpoints": [
                "/api/healthcare-gan/health",
                "/api/healthcare-gan/metrics", 
                "/api/healthcare-gan/train",
                "/api/healthcare-gan/generate",
                "/api/healthcare-gan/status"
            ]
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@healthcare_gan_bp.route('/test', methods=['GET'])
def test_integration():
    """Test Healthcare GAN integration"""
    try:
        # Test connectivity
        health = gan_client.health_check()
        
        # Test metrics endpoint
        metrics = gan_client.get_metrics()
        
        return jsonify({
            "test": "Healthcare GAN Integration Test",
            "health_check": health,
            "metrics_check": metrics,
            "integration_status": "working" if health["status"] == "healthy" else "error"
        }), 200
        
    except Exception as e:
        logger.error(f"Integration test error: {e}")
        return jsonify({"error": str(e)}), 500

# Error handlers for the blueprint
@healthcare_gan_bp.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Healthcare GAN endpoint not found"}), 404

@healthcare_gan_bp.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Healthcare GAN service internal error"}), 500