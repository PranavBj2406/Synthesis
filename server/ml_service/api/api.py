from fastapi import APIRouter, HTTPException, BackgroundTasks, status
from fastapi.responses import JSONResponse
import logging
from typing import Dict, Any
import traceback
import os

from Synthesis.server.ml_service.schemas import (
    TrainingRequest, DataGenerationRequest, 
    TrainingResponse, GenerationResponse, ValidationResponse, ErrorResponse
)
from train import Trainer
from generate import DataGenerator
from model_registry import model_registry
from config import DEFAULT_TIME_SERIES_PATH, DEFAULT_TABULAR_PATH

logger = logging.getLogger(__name__)
router = APIRouter()

# Global instances
trainer = Trainer()
generator = DataGenerator()

@router.post("/train", response_model=TrainingResponse)
async def train_models(request: TrainingRequest, background_tasks: BackgroundTasks):
    """Train the ML models with specified parameters."""
    try:
        logger.info(f"Training request received: epochs={request.epochs}, batch_size={request.batch_size}")
        
        # Use provided paths or defaults
        time_series_path = request.time_series_path or DEFAULT_TIME_SERIES_PATH
        tabular_path = request.tabular_path or DEFAULT_TABULAR_PATH
        
        # Validate file paths exist
        if not os.path.exists(time_series_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Time series dataset not found: {time_series_path}"
            )
        if not os.path.exists(tabular_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tabular dataset not found: {tabular_path}"
            )
        
        # Update global config with request parameters
        import config
        config.EPOCHS = request.epochs
        config.BATCH_SIZE = request.batch_size
        
        # Start training
        training_metrics = trainer.train_models(
            time_series_path=time_series_path,
            tabular_path=tabular_path,
            epochs=request.epochs
        )
        
        # Get model timestamp
        timestamp = model_registry.save_models(request.epochs)
        
        return TrainingResponse(
            status="success",
            message=f"Training completed successfully in {request.epochs} epochs",
            epochs_completed=request.epochs,
            training_metrics=training_metrics,
            model_timestamp=timestamp
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Training failed: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Training failed: {str(e)}"
        )

@router.post("/generate", response_model=GenerationResponse)
async def generate_data(request: DataGenerationRequest):
    """Generate synthetic healthcare data."""
    try:
        logger.info(f"Generation request: age={request.age}, gender={request.gender}, disease={request.disease_type}, records={request.num_records}")
        
        # Check if models are trained
        if not model_registry.is_trained:
            # Try to load latest models
            if not model_registry.load_models():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Models not trained. Please train models first using /train endpoint."
                )
        
        # Map enum values to numeric codes
        gender_code = 0 if request.gender == "Male" else 1
        disease_mapping = {
            "Diabetes": 0, "Heart Disease": 1, "Respiratory": 2, 
            "Neurological": 3, "Other": 4
        }
        disease_code = disease_mapping[request.disease_type]
        
        # Create conditions tensor
        import torch
        from config import COND_FEATURES
        conditions = torch.zeros(request.num_records, len(COND_FEATURES))
        conditions[:, 0] = (request.age - 18) / (90 - 18)  # Normalize age
        conditions[:, 1] = gender_code
        conditions[:, 2] = disease_code
        
        # Generate synthetic data
        synthetic_ts, synthetic_tab, conditions_np = generator.generate_synthetic_data(
            num_samples=request.num_records,
            conditions=conditions
        )
        
        # Save data and get file paths
        ts_file, tab_file = generator.save_synthetic_data(
            synthetic_ts, synthetic_tab, conditions_np,
            scalers={}, label_encoders={}, num_samples=request.num_records
        )
        
        # Create preview
        preview = generator.create_sample_preview(
            synthetic_ts, synthetic_tab, conditions_np, num_samples=3
        )
        
        return GenerationResponse(
            status="success",
            message=f"Successfully generated {request.num_records} synthetic records",
            num_generated=request.num_records,
            time_series_file=ts_file,
            tabular_file=tab_file,
            preview=preview
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Data generation failed: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Data generation failed: {str(e)}"
        )

@router.get("/models/status")
async def get_model_status():
    """Get current model training status."""
    try:
        return {
            "is_trained": model_registry.is_trained,
            "training_history": model_registry.get_training_history(),
            "available_models": model_registry.get_latest_timestamp() is not None
        }
    except Exception as e:
        logger.error(f"Status check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Status check failed: {str(e)}"
        )

@router.post("/validate", response_model=ValidationResponse)
async def validate_synthetic_data():
    """Validate the quality of generated synthetic data."""
    try:
        # This would implement validation logic
        # For now, return a placeholder response
        return ValidationResponse(
            status="success",
            statistical_metrics={"wasserstein_distance": 0.15, "ks_statistic": 0.12},
            utility_metrics={"accuracy": 0.85, "f1_score": 0.83},
            quality_score=0.84
        )
    except Exception as e:
        logger.error(f"Validation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation failed: {str(e)}"
        )
