from flask import Blueprint, request, jsonify, current_app
import uuid
import logging

try:
    from app.ml.client import HealthcareGANClient
except ImportError:
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

@healthcare_gan_bp.route('/models/status', methods=['GET'])
def model_status():
    """Get model training status"""
    try:
        result = gan_client.get_model_status()
        status_code = 200 if result["success"] else 500
        return jsonify(result), status_code
    except Exception as e:
        logger.error(f"Get model status error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@healthcare_gan_bp.route('/validate', methods=['POST'])
def validate_data():
    """Validate healthcare data"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        result = gan_client.validate_data(data)
        status_code = 200 if result["success"] else 400
        
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Validation error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@healthcare_gan_bp.route('/train', methods=['POST'])
def train_models():
    """Train diabetes and blood pressure prediction models"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"success": False, "error": "No training data provided"}), 400
        
        # Add request metadata
        if 'request_id' not in data:
            data['request_id'] = str(uuid.uuid4())
        
        result = gan_client.train_models(data)
        status_code = 200 if result["success"] else 500
        
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Training error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@healthcare_gan_bp.route('/predict', methods=['POST'])
def predict_diabetes():
    """Predict diabetes using trained model"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"success": False, "error": "No prediction data provided"}), 400
        
        # Add request metadata
        if 'request_id' not in data:
            data['request_id'] = str(uuid.uuid4())
        
        result = gan_client.predict_diabetes(data)
        status_code = 200 if result["success"] else 500
        
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@healthcare_gan_bp.route('/generate', methods=['POST'])
def generate_synthetic_data():
    """Generate synthetic healthcare data for testing/training
    
    Expected request body:
    {
        "num_samples": 100,
        "diabetes_ratio": 0.5,
        "hypertension_ratio": 0.7
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"success": False, "error": "No generation parameters provided"}), 400
        
        # Validate required fields
        if 'num_samples' not in data:
            return jsonify({"success": False, "error": "Missing required field: num_samples"}), 400
        
        # Set default values for optional fields
        generation_params = {
            "num_samples": data.get('num_samples'),
            "diabetes_ratio": data.get('diabetes_ratio', 0.5),
            "hypertension_ratio": data.get('hypertension_ratio', 0.5)
        }
        
        # Add request metadata if needed
        if 'request_id' in data:
            generation_params['request_id'] = data['request_id']
        else:
            generation_params['request_id'] = str(uuid.uuid4())
        
        result = gan_client.generate_synthetic_data(generation_params)
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
        model_status = gan_client.get_model_status()
        
        return jsonify({
            "service": "Healthcare GAN API Integration v2.0.0",
            "ml_service_health": health["status"],
            "model_status": model_status.get("data", {}),
            "endpoints": {
                "health": "/api/healthcare-gan/health",
                "model_status": "/api/healthcare-gan/models/status",
                "validate": "/api/healthcare-gan/validate",
                "train": "/api/healthcare-gan/train",
                "predict": "/api/healthcare-gan/predict",
                "generate": "/api/healthcare-gan/generate",
                "status": "/api/healthcare-gan/status"
            }
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@healthcare_gan_bp.route('/test', methods=['GET'])
def test_integration():
    """Test Healthcare GAN integration with all endpoints"""
    try:
        # Test health
        health = gan_client.health_check()
        
        # Test model status
        model_status = gan_client.get_model_status()
        
        return jsonify({
            "test": "Healthcare GAN Integration Test",
            "health_check": health,
            "model_status": model_status,
            "integration_status": "working" if health["status"] == "healthy" else "error",
            "api_version": "v2.0.0"
        }), 200
        
    except Exception as e:
        logger.error(f"Integration test error: {e}")
        return jsonify({"error": str(e)}), 500