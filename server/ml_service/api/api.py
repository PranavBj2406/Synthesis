# # from fastapi import APIRouter, HTTPException, BackgroundTasks
# # from fastapi.responses import JSONResponse
# # import logging
# # import traceback
# # from datetime import datetime
# # import asyncio

# # from schemas import (
# #     TrainingRequest, TrainingResponse, 
# #     DataGenerationRequest, GenerationResponse,
# #     DiabetesPredictionRequest, DiabetesPredictionResponse,
# #     ErrorResponse, ValidationResponse,
# #     DiabetesStatusEnum, BPStatusEnum
# # )
# # from train import DiabetesTrainer
# # from generate import DiabetesDataGenerator
# # from config import DEFAULT_TIME_SERIES_PATH, DEFAULT_TABULAR_PATH

# # logger = logging.getLogger(__name__)

# # router = APIRouter()

# # # Global instances
# # trainer = DiabetesTrainer()
# # generator = DiabetesDataGenerator()

# # @router.post("/train", response_model=TrainingResponse)
# # async def train_models(request: TrainingRequest, background_tasks: BackgroundTasks):
# #     """Train diabetes prediction models."""
# #     try:
# #         logger.info("Starting model training...")
        
# #         # Use default paths if not provided
# #         ts_path = request.time_series_path or DEFAULT_TIME_SERIES_PATH
# #         tab_path = request.tabular_path or DEFAULT_TABULAR_PATH
        
# #         # Train the model
# #         history = trainer.train_model(
# #             time_series_path=ts_path,
# #             tabular_path=tab_path,
# #             epochs=request.epochs,
# #             learning_rate=request.learning_rate
# #         )
        
# #         # Calculate final metrics
# #         final_accuracy = history['overall_acc'][-1] if history['overall_acc'] else 0.0
# #         diabetes_accuracy = history['diabetes_acc'][-1] if history['diabetes_acc'] else 0.0
# #         bp_accuracy = history['bp_acc'][-1] if history['bp_acc'] else 0.0
        
# #         return TrainingResponse(
# #             status="success",
# #             message="Model training completed successfully",
# #             epochs_completed=request.epochs,
# #             final_accuracy=final_accuracy,
# #             diabetes_accuracy=diabetes_accuracy,
# #             bp_accuracy=bp_accuracy,
# #             training_metrics=history,
# #             model_timestamp=datetime.now().isoformat()
# #         )
        
# #     except Exception as e:
# #         logger.error(f"Training failed: {str(e)}")
# #         logger.error(traceback.format_exc())
# #         raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")

# # @router.post("/predict", response_model=DiabetesPredictionResponse)
# # async def predict_diabetes(request: DiabetesPredictionRequest):
# #     """Predict diabetes and blood pressure status."""
# #     try:
# #         # Prepare input data
# #         tabular_features = [
# #             request.age, request.bmi, request.average_rbs, request.hba1c,
# #             request.respiratory_rate, request.heart_rate, request.spo2
# #         ]
        
# #         # Make prediction
# #         result = trainer.predict(request.rbs_sequence, tabular_features)
        
# #         # Calculate confidence score
# #         confidence = (abs(result['diabetes_probability'] - 0.5) + abs(result['bp_probability'] - 0.5)) / 2
        
# #         return DiabetesPredictionResponse(
# #             diabetes_probability=result['diabetes_probability'],
# #             diabetes_prediction=DiabetesStatusEnum.diabetic if result['diabetes_prediction'] == 1 else DiabetesStatusEnum.non_diabetic,
# #             bp_probability=result['bp_probability'],
# #             bp_prediction=BPStatusEnum.hypertensive if result['bp_prediction'] == 1 else BPStatusEnum.normal,
# #             confidence_score=confidence
# #         )
        
# #     except Exception as e:
# #         logger.error(f"Prediction failed: {str(e)}")
# #         logger.error(traceback.format_exc())
# #         raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

# # @router.post("/generate", response_model=GenerationResponse)
# # async def generate_synthetic_data(request: DataGenerationRequest):
# #     """Generate synthetic diabetes data."""
# #     try:
# #         logger.info(f"Generating {request.num_samples} synthetic samples...")
        
# #         # Generate synthetic data
# #         result = generator.generate_synthetic_data(
# #             num_samples=request.num_samples,
# #             diabetes_ratio=request.diabetes_ratio,
# #             hypertension_ratio=request.hypertension_ratio
# #         )
        
# #         return GenerationResponse(
# #             status="success",
# #             message=f"Successfully generated {request.num_samples} synthetic samples",
# #             num_generated=request.num_samples,
# #             timeseries_file=result['timeseries_file'],
# #             tabular_file=result['tabular_file'],
# #             preview=result['preview']
# #         )
        
# #     except Exception as e:
# #         logger.error(f"Data generation failed: {str(e)}")
# #         logger.error(traceback.format_exc())
# #         raise HTTPException(status_code=500, detail=f"Data generation failed: {str(e)}")

# # @router.get("/validate", response_model=ValidationResponse)
# # async def validate_data():
# #     """Validate the current datasets."""
# #     try:
# #         # Basic validation metrics
# #         statistical_metrics = {
# #             "data_quality": "good",
# #             "completeness": 0.95,
# #             "consistency": 0.98
# #         }
        
# #         utility_metrics = {
# #             "feature_coverage": 0.92,
# #             "target_balance": 0.85,
# #             "distribution_similarity": 0.88
# #         }
        
# #         quality_score = (
# #             statistical_metrics["completeness"] + 
# #             statistical_metrics["consistency"] + 
# #             utility_metrics["feature_coverage"]
# #         ) / 3
        
# #         return ValidationResponse(
# #             status="success",
# #             statistical_metrics=statistical_metrics,
# #             utility_metrics=utility_metrics,
# #             quality_score=quality_score
# #         )
        
# #     except Exception as e:
# #         logger.error(f"Validation failed: {str(e)}")
# #         raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")

# # @router.get("/models/status")
# # async def get_model_status():
# #     """Get current model training status."""
# #     try:
# #         is_trained = trainer.model is not None
        
# #         return {
# #             "status": "success",
# #             "model_trained": is_trained,
# #             "model_type": "DiabetesPredictor" if is_trained else None,
# #             "last_updated": datetime.now().isoformat()
# #         }
        
# #     except Exception as e:
# #         logger.error(f"Status check failed: {str(e)}")
# #         raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")
# from fastapi import APIRouter, HTTPException, BackgroundTasks
# from fastapi.responses import JSONResponse
# import logging
# import traceback
# from datetime import datetime
# import numpy as np
# import pandas as pd
# from scipy import stats
# from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# from schemas import (
#     TrainingRequest, TrainingResponse,
#     DataGenerationRequest, GenerationResponse,
#     DiabetesPredictionRequest, DiabetesPredictionResponse,
#     ValidationResponse,
#     DiabetesStatusEnum, BPStatusEnum,
#     GANTrainingRequest, GANTrainingResponse
# )

# from train import DiabetesTrainer
# from generate import DiabetesDataGenerator
# from gan_trainer import GANTrainer
# from config import DEFAULT_TIME_SERIES_PATH, DEFAULT_TABULAR_PATH

# logger = logging.getLogger(__name__)

# # Initialize router FIRST
# router = APIRouter()

# # Global instances
# trainer = DiabetesTrainer()
# generator = DiabetesDataGenerator()
# gan_trainer_instance = GANTrainer()

# # ==================== SUPERVISED MODEL TRAINING ====================
# @router.post("/train", response_model=TrainingResponse)
# async def train_models(request: TrainingRequest):
#     """Train diabetes prediction models."""
#     try:
#         logger.info("Starting model training...")
#         logger.info(f"Using paths - TS: {DEFAULT_TIME_SERIES_PATH}, Tabular: {DEFAULT_TABULAR_PATH}")
        
#         # Use default paths
#         ts_path = DEFAULT_TIME_SERIES_PATH
#         tab_path = DEFAULT_TABULAR_PATH
        
#         # Train the model
#         history = trainer.train_model(
#             time_series_path=ts_path,
#             tabular_path=tab_path,
#             epochs=request.epochs,
#             learning_rate=request.learning_rate
#         )
        
#         # Calculate final metrics
#         final_accuracy = history['overall_acc'][-1] if history['overall_acc'] else 0.0
#         diabetes_accuracy = history['diabetes_acc'][-1] if history['diabetes_acc'] else 0.0
#         bp_accuracy = history['bp_acc'][-1] if history['bp_acc'] else 0.0
        
#         return TrainingResponse(
#             status="success",
#             message="Model training completed successfully",
#             epochs_completed=request.epochs,
#             final_accuracy=final_accuracy,
#             diabetes_accuracy=diabetes_accuracy,
#             bp_accuracy=bp_accuracy,
#             training_metrics=history,
#             model_timestamp=datetime.now().isoformat()
#         )
        
#     except Exception as e:
#         logger.error(f"Training failed: {str(e)}")
#         logger.error(traceback.format_exc())
#         raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")

# # ==================== GAN MODEL TRAINING ====================
# @router.post("/train-gan", response_model=GANTrainingResponse)
# async def train_gan_models(request: GANTrainingRequest):
#     """Train GAN models for synthetic data generation."""
#     try:
#         logger.info("Starting GAN model training...")
#         logger.info(f"Using paths - TS: {DEFAULT_TIME_SERIES_PATH}, Tabular: {DEFAULT_TABULAR_PATH}")
        
#         # Use default paths
#         ts_path = DEFAULT_TIME_SERIES_PATH
#         tab_path = DEFAULT_TABULAR_PATH
        
#         # Train GAN models
#         history = gan_trainer_instance.train_gan(
#             time_series_path=ts_path,
#             tabular_path=tab_path,
#             epochs=request.epochs
#         )
        
#         return GANTrainingResponse(
#             status="success",
#             message="GAN model training completed successfully",
#             epochs_completed=request.epochs,
#             training_metrics=history,
#             model_timestamp=datetime.now().isoformat()
#         )
        
#     except Exception as e:
#         logger.error(f"GAN training failed: {str(e)}")
#         logger.error(traceback.format_exc())
#         raise HTTPException(status_code=500, detail=f"GAN training failed: {str(e)}")

# # ==================== PREDICTION ====================
# @router.post("/predict", response_model=DiabetesPredictionResponse)
# async def predict_diabetes(request: DiabetesPredictionRequest):
#     """Predict diabetes and blood pressure status."""
#     try:
#         # Prepare input data
#         tabular_features = [
#             request.age / 55.0,  # Normalize
#             request.bmi / 45.0,
#             request.average_rbs / 400.0,
#             request.hba1c / 7.0,
#             request.respiratory_rate / 18.0,
#             request.heart_rate / 100.0,
#             request.spo2 / 100.0,
#             0.5,  # Placeholder for systolic (normalized)
#             0.5   # Placeholder for diastolic (normalized)
#         ]
        
#         # Normalize RBS sequence
#         normalized_rbs = [val / 400.0 for val in request.rbs_sequence]
        
#         # Make prediction
#         result = trainer.predict(normalized_rbs, tabular_features)
        
#         # Calculate confidence score
#         confidence = (abs(result['diabetes_probability'] - 0.5) + abs(result['bp_probability'] - 0.5)) / 2
        
#         return DiabetesPredictionResponse(
#             diabetes_probability=result['diabetes_probability'],
#             diabetes_prediction=DiabetesStatusEnum.diabetic if result['diabetes_prediction'] == 1 else DiabetesStatusEnum.non_diabetic,
#             bp_probability=result['bp_probability'],
#             bp_prediction=BPStatusEnum.hypertensive if result['bp_prediction'] == 1 else BPStatusEnum.normal,
#             confidence_score=confidence
#         )
        
#     except Exception as e:
#         logger.error(f"Prediction failed: {str(e)}")
#         logger.error(traceback.format_exc())
#         raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

# # ==================== DATA GENERATION ====================
# @router.post("/generate", response_model=GenerationResponse)
# async def generate_synthetic_data(request: DataGenerationRequest):
#     """Generate synthetic diabetes data using GAN or statistical fallback."""
#     try:
#         logger.info(f"Generating {request.num_samples} synthetic samples...")
        
#         # Generate synthetic data
#         result = generator.generate_synthetic_data(
#             num_samples=request.num_samples,
#             diabetes_ratio=request.diabetes_ratio,
#             hypertension_ratio=request.hypertension_ratio
#         )
        
#         return GenerationResponse(
#             status="success",
#             message=f"Successfully generated {request.num_samples} synthetic samples",
#             num_generated=request.num_samples,
#             timeseries_file=result['timeseries_file'],
#             tabular_file=result['tabular_file'],
#             preview=result['preview']
#         )
        
#     except Exception as e:
#         logger.error(f"Data generation failed: {str(e)}")
#         logger.error(traceback.format_exc())
#         raise HTTPException(status_code=500, detail=f"Data generation failed: {str(e)}")

# # ==================== VALIDATION ====================
# @router.get("/validate", response_model=ValidationResponse)
# async def validate_data():
#     """Comprehensive validation of datasets using advanced statistical methods."""
#     try:
#         logger.info("Starting comprehensive data validation...")
        
#         # Load datasets
#         ts_df = pd.read_csv(DEFAULT_TIME_SERIES_PATH)
#         tab_df = pd.read_csv(DEFAULT_TABULAR_PATH)
        
#         # Statistical Metrics
#         statistical_metrics = {
#             "completeness": _calculate_completeness(ts_df, tab_df),
#             "consistency": _calculate_consistency(ts_df, tab_df),
#             "accuracy": _calculate_accuracy(tab_df),
#             "distribution_normality": _test_normality(tab_df),
#             "outlier_percentage": _detect_outliers(tab_df),
#             "correlation_validity": _validate_correlations(tab_df)
#         }
        
#         # Utility Metrics
#         utility_metrics = {
#             "feature_coverage": _calculate_feature_coverage(tab_df),
#             "target_balance": _calculate_target_balance(tab_df),
#             "temporal_consistency": _validate_temporal_consistency(ts_df),
#             "clinical_validity": _validate_clinical_ranges(tab_df),
#             "data_diversity": _calculate_diversity(tab_df)
#         }
        
#         # Overall Quality Score (weighted average)
#         quality_score = (
#             statistical_metrics["completeness"] * 0.20 +
#             statistical_metrics["consistency"] * 0.20 +
#             statistical_metrics["accuracy"] * 0.15 +
#             utility_metrics["feature_coverage"] * 0.15 +
#             utility_metrics["target_balance"] * 0.15 +
#             utility_metrics["clinical_validity"] * 0.15
#         )
        
#         logger.info(f"Validation completed. Quality score: {quality_score:.4f}")
        
#         return ValidationResponse(
#             status="success",
#             statistical_metrics=statistical_metrics,
#             utility_metrics=utility_metrics,
#             quality_score=round(quality_score, 4)
#         )
        
#     except Exception as e:
#         logger.error(f"Validation failed: {str(e)}")
#         logger.error(traceback.format_exc())
#         raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")

# # ==================== MODEL STATUS ====================
# @router.get("/models/status")
# async def get_model_status():
#     """Get current model training status."""
#     try:
#         is_trained = trainer.model is not None
#         gan_models_loaded = generator.models_loaded
        
#         return {
#             "status": "success",
#             "supervised_model_trained": is_trained,
#             "gan_models_loaded": gan_models_loaded,
#             "model_type": "DiabetesPredictor" if is_trained else None,
#             "generation_method": "GAN" if gan_models_loaded else "Statistical",
#             "last_updated": datetime.now().isoformat(),
#             "dataset_paths": {
#                 "time_series": DEFAULT_TIME_SERIES_PATH,
#                 "tabular": DEFAULT_TABULAR_PATH
#             }
#         }
        
#     except Exception as e:
#         logger.error(f"Status check failed: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")

# # ==================== VALIDATION HELPER FUNCTIONS ====================
# def _calculate_completeness(ts_df, tab_df):
#     """Calculate data completeness."""
#     ts_completeness = 1 - (ts_df.isnull().sum().sum() / (ts_df.shape[0] * ts_df.shape[1]))
#     tab_completeness = 1 - (tab_df.isnull().sum().sum() / (tab_df.shape[0] * tab_df.shape[1]))
#     return round((ts_completeness + tab_completeness) / 2, 4)

# def _calculate_consistency(ts_df, tab_df):
#     """Check consistency between time series and tabular data."""
#     ts_patients = set(ts_df['patient_id'].unique())
#     tab_patients = set(tab_df['patient_id'].unique())
#     overlap = len(ts_patients.intersection(tab_patients))
#     consistency = overlap / max(len(ts_patients), len(tab_patients))
#     return round(consistency, 4)

# def _calculate_accuracy(tab_df):
#     """Validate data accuracy based on business rules."""
#     correct_outcomes = 0
#     total = len(tab_df)
    
#     for _, row in tab_df.iterrows():
#         if row['average_rbs'] > 200 and row['hba1c'] > 6.7:
#             if row['diabetes'] == 1:
#                 correct_outcomes += 1
#         elif row['average_rbs'] < 200 and row['hba1c'] < 5.7:
#             if row['diabetes'] == 0:
#                 correct_outcomes += 1
#         else:
#             correct_outcomes += 1
    
#     return round(correct_outcomes / total, 4)

# def _test_normality(tab_df):
#     """Test if numeric columns follow expected distributions."""
#     numeric_cols = ['age', 'bmi', 'average_rbs', 'hba1c', 'heart_rate', 'respiratory_rate', 'spo2']
#     normality_scores = []
    
#     for col in numeric_cols:
#         if col in tab_df.columns:
#             _, p_value = stats.shapiro(tab_df[col].sample(min(5000, len(tab_df))))
#             normality_scores.append(1 if p_value > 0.01 else 0.5)
    
#     return round(np.mean(normality_scores), 4)

# def _detect_outliers(tab_df):
#     """Detect outliers using IQR method."""
#     numeric_cols = ['age', 'bmi', 'average_rbs', 'hba1c', 'heart_rate', 'respiratory_rate', 'spo2']
#     total_values = 0
#     outlier_count = 0
    
#     for col in numeric_cols:
#         if col in tab_df.columns:
#             Q1 = tab_df[col].quantile(0.25)
#             Q3 = tab_df[col].quantile(0.75)
#             IQR = Q3 - Q1
#             outliers = ((tab_df[col] < (Q1 - 1.5 * IQR)) | (tab_df[col] > (Q3 + 1.5 * IQR))).sum()
#             outlier_count += outliers
#             total_values += len(tab_df[col])
    
#     return round(outlier_count / total_values, 4)

# def _validate_correlations(tab_df):
#     """Validate expected correlations between features."""
#     diabetes_rbs_corr = abs(tab_df['diabetes'].corr(tab_df['average_rbs']))
#     diabetes_hba1c_corr = abs(tab_df['diabetes'].corr(tab_df['hba1c']))
#     diabetes_bmi_corr = abs(tab_df['diabetes'].corr(tab_df['bmi']))
    
#     avg_correlation = (diabetes_rbs_corr + diabetes_hba1c_corr + diabetes_bmi_corr) / 3
#     return round(avg_correlation, 4)

# def _calculate_feature_coverage(tab_df):
#     """Check if all required features are present and valid."""
#     required_features = ['age', 'bmi', 'average_rbs', 'hba1c', 'hypertension',
#                         'respiratory_rate', 'heart_rate', 'spo2', 'diabetes', 'bp_status']
#     present_features = sum([1 for feat in required_features if feat in tab_df.columns])
#     return round(present_features / len(required_features), 4)

# def _calculate_target_balance(tab_df):
#     """Check balance of target variables."""
#     diabetes_balance = min(tab_df['diabetes'].value_counts()) / max(tab_df['diabetes'].value_counts())
#     bp_balance = min(tab_df['bp_status'].value_counts()) / max(tab_df['bp_status'].value_counts())
#     return round((diabetes_balance + bp_balance) / 2, 4)

# def _validate_temporal_consistency(ts_df):
#     """Validate temporal patterns in time series data."""
#     ts_df_sorted = ts_df.sort_values(['patient_id', 'timestamp'])
#     consistency_scores = []
    
#     for patient_id in ts_df_sorted['patient_id'].unique()[:100]:
#         patient_data = ts_df_sorted[ts_df_sorted['patient_id'] == patient_id]
#         if len(patient_data) > 1:
#             is_sequential = patient_data['timestamp'].is_monotonic_increasing
#             consistency_scores.append(1.0 if is_sequential else 0.5)
    
#     return round(np.mean(consistency_scores) if consistency_scores else 1.0, 4)

# def _validate_clinical_ranges(tab_df):
#     """Validate if values are within clinically acceptable ranges."""
#     valid_count = 0
#     total_count = 0
    
#     validations = {
#         'age': (30, 55),
#         'bmi': (18.5, 45.0),
#         'average_rbs': (100.0, 400.0),
#         'hba1c': (5.72, 7.0),
#         'respiratory_rate': (12, 18),
#         'heart_rate': (70, 100),
#         'spo2': (95.0, 100.0)
#     }
    
#     for col, (min_val, max_val) in validations.items():
#         if col in tab_df.columns:
#             valid_count += ((tab_df[col] >= min_val) & (tab_df[col] <= max_val)).sum()
#             total_count += len(tab_df[col])
    
#     return round(valid_count / total_count, 4)

# def _calculate_diversity(tab_df):
#     """Calculate diversity of data (entropy-based)."""
#     numeric_cols = ['age', 'bmi', 'average_rbs', 'hba1c']
#     diversity_scores = []
    
#     for col in numeric_cols:
#         if col in tab_df.columns:
#             binned = pd.cut(tab_df[col], bins=10, labels=False)
#             value_counts = binned.value_counts(normalize=True)
#             entropy = -np.sum(value_counts * np.log2(value_counts + 1e-10))
#             max_entropy = np.log2(10)
#             diversity_scores.append(entropy / max_entropy)
    
#     return round(np.mean(diversity_scores), 4)
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import logging
import traceback
from datetime import datetime

from schemas import (
    GANTrainingRequest, GANTrainingResponse,
    DataGenerationRequest, GenerationResponse
)
from gan_trainer import GANTrainer
from generate import DiabetesDataGenerator
from config import DEFAULT_TIME_SERIES_PATH, DEFAULT_TABULAR_PATH

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter()

# Global instances
gan_trainer_instance = GANTrainer()
generator = DiabetesDataGenerator()

# ==================== GAN TRAINING (ONLY ENDPOINT) ====================
@router.post("/train/gan", response_model=GANTrainingResponse)
async def train_gan_models(request: GANTrainingRequest):
    """
    Train GAN models for synthetic data generation using GitHub datasets.
    This is the ONLY training endpoint available.
    """
    try:
        logger.info("=" * 80)
        logger.info("Starting GAN model training...")
        logger.info(f"Epochs: {request.epochs} | Batch size: {request.batch_size}")
        logger.info(f"Using GitHub dataset URLs (no local fallback)")
        logger.info("=" * 80)

        # ALWAYS use GitHub URLs (no local override)
        ts_path = DEFAULT_TIME_SERIES_PATH
        tab_path = DEFAULT_TABULAR_PATH

        # Train GAN models
        history = gan_trainer_instance.train_gan(
            time_series_path=ts_path,
            tabular_path=tab_path,
            epochs=request.epochs
        )

        return GANTrainingResponse(
            status="success",
            message="GAN model training completed successfully",
            epochs_completed=request.epochs,
            training_metrics=history,
            model_timestamp=datetime.now().isoformat()
        )

    except RuntimeError as e:
        # Dataset loading error (GitHub fetch failed)
        error_msg = str(e)
        if "Failed to load dataset from GitHub" in error_msg:
            logger.error(f"Dataset fetch error: {error_msg}")
            raise HTTPException(
                status_code=503,
                detail={
                    "status": "error",
                    "message": "Failed to load dataset from GitHub",
                    "url": ts_path if "time series" in error_msg.lower() else tab_path
                }
            )
        raise HTTPException(status_code=500, detail=f"Training failed: {error_msg}")
    
    except Exception as e:
        logger.error(f"GAN training failed: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"GAN training failed: {str(e)}")

# ==================== REJECT ALL OTHER TRAINING ROUTES ====================
@router.post("/train")
@router.post("/train/model")
@router.post("/train/supervised")
async def reject_other_training():
    """Reject all non-GAN training endpoints."""
    raise HTTPException(
        status_code=405,
        detail={
            "error": "Only gan-train is supported in this deployment. Use /api/v1/train/gan."
        }
    )

# ==================== DATA GENERATION ====================
@router.post("/generate", response_model=GenerationResponse)
async def generate_synthetic_data(request: DataGenerationRequest):
    """
    Generate synthetic diabetes data using trained GAN models.
    REQUIRES GAN models to be trained first. NO STATISTICAL FALLBACK.
    """
    try:
        logger.info(f"Generating {request.num_samples} synthetic samples...")

        # Check if GAN models are loaded
        if not generator.models_loaded:
            logger.error("GAN models not available for generation")
            raise HTTPException(
                status_code=503,
                detail={
                    "status": "error",
                    "message": "GAN models not available. Please train using /api/v1/train/gan first."
                }
            )

        # Generate synthetic data using GAN
        result = generator.generate_synthetic_data(
            num_samples=request.num_samples,
            diabetes_ratio=request.diabetes_ratio,
            hypertension_ratio=request.hypertension_ratio
        )

        return GenerationResponse(
            status="success",
            message=f"Successfully generated {request.num_samples} synthetic samples using GAN",
            num_generated=request.num_samples,
            timeseries_file=result['timeseries_file'],
            tabular_file=result['tabular_file'],
            preview=result['preview']
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Data generation failed: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Data generation failed: {str(e)}")

# ==================== MODEL STATUS ====================
@router.get("/models/status")
async def get_model_status():
    """Get current GAN model training status."""
    try:
        gan_models_loaded = generator.models_loaded

        return {
            "status": "success",
            "gan_models_loaded": gan_models_loaded,
            "generation_method": "GAN" if gan_models_loaded else "Not Available",
            "training_endpoint": "/api/v1/train/gan",
            "last_updated": datetime.now().isoformat(),
            "dataset_paths": {
                "time_series": DEFAULT_TIME_SERIES_PATH,
                "tabular": DEFAULT_TABULAR_PATH
            }
        }
    except Exception as e:
        logger.error(f"Status check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")

# ==================== HEALTH CHECK ====================
@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
