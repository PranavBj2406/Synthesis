import requests
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class HealthcareGANClient:
    """Client for Healthcare GAN API v2.0.0"""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url.rstrip('/')
        self.api_prefix = "/api/v1"  # NEW: API version prefix
        self.timeout = 60
    
    def _get_url(self, endpoint: str) -> str:
        """Helper to construct full URL with API prefix"""
        # Remove leading slash from endpoint if present
        endpoint = endpoint.lstrip('/')
        return f"{self.base_url}{self.api_prefix}/{endpoint}"
    
    def health_check(self) -> Dict[str, Any]:
        """GET /health - Health Check (no /api/v1 prefix)"""
        try:
            # Health check is at root level, not under /api/v1
            response = requests.get(f"{self.base_url}/health", timeout=10)
            response.raise_for_status()
            return {"status": "healthy", "details": response.json()}
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def get_model_status(self) -> Dict[str, Any]:
        """GET /api/v1/models/status - Get Model Status"""
        try:
            response = requests.get(self._get_url("models/status"), timeout=30)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except Exception as e:
            logger.error(f"Get model status failed: {e}")
            return {"success": False, "error": str(e)}
    
    def validate_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """GET /api/v1/validate - Validate Data"""
        try:
            # Validation might use query params or JSON body
            response = requests.get(
                self._get_url("validate"), 
                params=data,  # Try as query params first
                timeout=30
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except Exception as e:
            logger.error(f"Validate data failed: {e}")
            return {"success": False, "error": str(e)}
    
    def train_models(self, training_data: Dict[str, Any]) -> Dict[str, Any]:
        """POST /api/v1/train - Train Models"""
        try:
            response = requests.post(
                self._get_url("train"), 
                json=training_data, 
                timeout=self.timeout
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except Exception as e:
            logger.error(f"Train models failed: {e}")
            return {"success": False, "error": str(e)}
    
    def predict_diabetes(self, prediction_data: Dict[str, Any]) -> Dict[str, Any]:
        """POST /api/v1/predict - Predict Diabetes"""
        try:
            response = requests.post(
                self._get_url("predict"), 
                json=prediction_data, 
                timeout=30
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except Exception as e:
            logger.error(f"Predict diabetes failed: {e}")
            return {"success": False, "error": str(e)}
    
    def generate_synthetic_data(self, generation_params: Dict[str, Any]) -> Dict[str, Any]:
        """POST /api/v1/generate - Generate Synthetic Data"""
        try:
            response = requests.post(
                self._get_url("generate"), 
                json=generation_params, 
                timeout=self.timeout
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except Exception as e:
            logger.error(f"Generate synthetic data failed: {e}")
            return {"success": False, "error": str(e)}
