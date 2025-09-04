import logging
import torch
from datetime import datetime
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from schemas import *
from train import Trainer
from generate import DataGenerator
from model_registry import model_registry
from config import *

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"{LOGS_DIR}/api.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    logger.info("Starting Healthcare GAN API")
    
    # Try to load existing models
    if model_registry.load_models():
        logger.info("Loaded existing trained models")
    else:
        logger.info("No pre-trained models found")
    
    yield
    
    logger.info("Shutting down Healthcare GAN API")

app = FastAPI(
    title="Healthcare GAN API",
    description="API for generating synthetic healthcare data using GANs",
    version="1.0.0",
    lifespan=lifespan
)

trainer = Trainer()
generator = DataGenerator()

@app.post("/train", response_model=TrainResponse)
async def train_models(request: TrainRequest):
    """Train GAN models on provided healthcare data."""
    try:
        logger.info(f"Starting training with {request.epochs} epochs")
        
        # Train models
        training_history = trainer.train_models(
            request.time_series_path,
            request.tabular_path, 
            request.epochs
        )
        
        # Get timestamp from model registry
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        return TrainResponse(
            message="Training completed successfully",
            timestamp=timestamp,
            training_history=training_history,
            epochs=request.epochs
        )
        
    except FileNotFoundError as e:
        logger.error(f"File not found: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Data file not found: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Training failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Training failed: {str(e)}"
        )

@app.post("/generate", response_model=GenerateResponse)
async def generate_data(request: GenerateRequest):
    """Generate synthetic healthcare data."""
    try:
        logger.info(f"Generating {request.num_samples} synthetic samples")
        
        # Prepare conditions if provided
        conditions = None
        if any([request.age, request.gender, request.disease]):
            conditions = torch.zeros(request.num_samples, len(COND_FEATURES))
            
            # Set age
            if request.age is not None:
                conditions[:, 0] = request.age / 100  # Normalize
            else:
                conditions[:, 0] = torch.rand(request.num_samples) * 0.9 + 0.05
                
            # Set gender
            if request.gender is not None:
                gender_val = 0 if request.gender.lower() == 'male' else 1
                conditions[:, 1] = gender_val
            else:
                conditions[:, 1] = torch.randint(0, 2, (request.num_samples,)).float()
                
            # Set disease
            if request.disease is not None:
                disease_map = {"diabetes": 0, "heart disease": 1, "respiratory": 2, "neurological": 3, "other": 4}
                disease_val = disease_map.get(request.disease.lower(), 4)
                conditions[:, 2] = disease_val
            else:
                conditions[:, 2] = torch.randint(0, 5, (request.num_samples,)).float()
        
        # Generate synthetic data
        synthetic_ts, synthetic_tab, conditions_np = generator.generate_synthetic_data(
            request.num_samples, conditions
        )
        
        # Save data (note: would need access to scalers and label_encoders from training)
        # For now, we'll save raw data
        from data_utils import DataPreprocessor
        preprocessor = DataPreprocessor()
        
        ts_file, tab_file = generator.save_synthetic_data(
            synthetic_ts, synthetic_tab, conditions_np,
            {}, {},  # Empty scalers and encoders for now
            request.num_samples
        )
        
        # Create preview
        preview = generator.create_sample_preview(synthetic_ts, synthetic_tab, conditions_np)
        
        return GenerateResponse(
            message=f"Successfully generated {request.num_samples} synthetic samples",
            num_generated=request.num_samples,
            files={
                "time_series": ts_file,
                "tabular": tab_file
            },
            preview=preview
        )
        
    except RuntimeError as e:
        logger.error(f"Models not trained: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Models not trained. Please train models first using /train endpoint."
        )
    except Exception as e:
        logger.error(f"Generation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Data generation failed: {str(e)}"
        )

@app.get("/metrics", response_model=MetricsResponse)
async def get_metrics():
    """Get training metrics and model information."""
    try:
        training_history = model_registry.get_training_history()
        
        model_info = {
            "seq_length": SEQ_LENGTH,
            "latent_dim": LATENT_DIM,
            "hidden_dim": HIDDEN_DIM,
            "features": FEATURES,
            "tabular_features": TABULAR_FEATURES,
            "cond_features": COND_FEATURES
        }
        
        return MetricsResponse(
            training_history=training_history,
            model_info=model_info,
            device=str(model_registry.device),
            is_trained=model_registry.is_trained
        )
        
    except Exception as e:
        logger.error(f"Error getting metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving metrics: {str(e)}"
        )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        device=str(model_registry.device),
        models_loaded=model_registry.is_trained,
        timestamp=datetime.now().isoformat()
    )

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Internal server error", "detail": str(exc)}
    )
