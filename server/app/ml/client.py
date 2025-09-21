import requests
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class HealthcareGANClient:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url.rstrip('/')
        self.timeout = 60  # Longer timeout for training/generation
    
    def health_check(self) -> Dict[str, Any]:
        """GET /health - Health Check"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            response.raise_for_status()
            return {"status": "healthy", "details": response.json()}
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def get_metrics(self) -> Dict[str, Any]:
        """GET /metrics - Get Metrics"""
        try:
            response = requests.get(f"{self.base_url}/metrics", timeout=30)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except Exception as e:
            logger.error(f"Get metrics failed: {e}")
            return {"success": False, "error": str(e)}
    
    def train_models(self, training_data: Dict[str, Any]) -> Dict[str, Any]:
        """POST /train - Train Models"""
        try:
            response = requests.post(
                f"{self.base_url}/train", 
                json=training_data, 
                timeout=self.timeout
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except Exception as e:
            logger.error(f"Train models failed: {e}")
            return {"success": False, "error": str(e)}
    
    def generate_data(self, generation_params: Dict[str, Any]) -> Dict[str, Any]:
        """POST /generate - Generate Data"""
        try:
            response = requests.post(
                f"{self.base_url}/generate", 
                json=generation_params, 
                timeout=self.timeout
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except Exception as e:
            logger.error(f"Generate data failed: {e}")
            return {"success": False, "error": str(e)}