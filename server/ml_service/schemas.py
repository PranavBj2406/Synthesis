
# from pydantic import BaseModel, Field, validator, ConfigDict
# from typing import Optional, List, Dict, Any
# from enum import Enum

# # ==================== ENUMS ====================
# class DiabetesStatusEnum(str, Enum):
#     """Diabetes status classification."""
#     non_diabetic = "Non-Diabetic"
#     diabetic = "Diabetic"

# class BPStatusEnum(str, Enum):
#     """Blood pressure status classification."""
#     normal = "Normal"
#     hypertensive = "Hypertensive"

# # ==================== PREDICTION SCHEMAS ====================
# class DiabetesPredictionRequest(BaseModel):
#     """Request for diabetes and blood pressure prediction."""
#     model_config = ConfigDict(
#         json_schema_extra={
#             "example": {
#                 "age": 45,
#                 "bmi": 28.5,
#                 "average_rbs": 280.5,
#                 "hba1c": 6.8,
#                 "respiratory_rate": 15,
#                 "heart_rate": 82,
#                 "spo2": 97.5,
#                 "rbs_sequence": [250.0, 270.0, 290.0, 310.0, 300.0, 280.0, 290.0, 285.0, 275.0, 270.0, 265.0, 260.0, 255.0]
#             }
#         }
#     )
    
#     age: int = Field(..., ge=30, le=55, description="Patient age (30-55 years)", example=45)
#     bmi: float = Field(..., ge=18.5, le=45.0, description="Body Mass Index (18.5-45.0)", example=28.5)
#     average_rbs: float = Field(..., ge=100.0, le=400.0, description="Average RBS level (100-400 mg/dL)", example=280.5)
#     hba1c: float = Field(..., ge=5.72, le=7.0, description="HbA1c percentage (5.72-7.0%)", example=6.8)
#     respiratory_rate: int = Field(..., ge=12, le=18, description="Respiratory rate (12-18 breaths/min)", example=15)
#     heart_rate: int = Field(..., ge=70, le=100, description="Heart rate (70-100 bpm)", example=82)
#     spo2: float = Field(..., ge=95.0, le=100.0, description="SpO2 percentage (95-100%)", example=97.5)
#     rbs_sequence: List[float] = Field(
#         ..., 
#         description="Hourly RBS readings (13 values from 6 AM to 6 PM)",
#         example=[250.0, 270.0, 290.0, 310.0, 300.0, 280.0, 290.0, 285.0, 275.0, 270.0, 265.0, 260.0, 255.0]
#     )

#     @validator('rbs_sequence')
#     def validate_rbs_sequence(cls, v):
#         if len(v) != 13:
#             raise ValueError('RBS sequence must contain exactly 13 hourly readings (6 AM to 6 PM)')
#         if not all(100.0 <= val <= 400.0 for val in v):
#             raise ValueError('All RBS values must be between 100.0 and 400.0 mg/dL')
#         return v

# class DiabetesPredictionResponse(BaseModel):
#     """Response for diabetes and blood pressure prediction."""
#     diabetes_probability: float = Field(..., description="Probability of diabetes (0-1)", example=0.85)
#     diabetes_prediction: DiabetesStatusEnum = Field(..., description="Diabetes classification", example="Diabetic")
#     bp_probability: float = Field(..., description="Probability of hypertension (0-1)", example=0.72)
#     bp_prediction: BPStatusEnum = Field(..., description="Blood pressure classification", example="Hypertensive")
#     confidence_score: float = Field(..., description="Overall prediction confidence (0-1)", example=0.78)

# # ==================== SUPERVISED TRAINING SCHEMAS ====================
# class TrainingRequest(BaseModel):
#     """
#     Request for SUPERVISED model training (Diabetes Prediction Model).
#     This trains the model that predicts diabetes and BP status from patient data.
#     Recommended: 50-100 epochs (trains in 2-5 minutes).
#     """
#     model_config = ConfigDict(
#         protected_namespaces=(),
#         json_schema_extra={
#             "example": {
#                 "epochs": 50,
#                 "batch_size": 32,
#                 "learning_rate": 0.001,
#                 "dropout_rate": 0.3,
#                 "hidden_dim": 128,
#                 "use_attention": True
#             }
#         }
#     )
    
#     epochs: int = Field(
#         default=50, 
#         ge=10, 
#         le=300, 
#         description="Training epochs (10-300). Recommended: 50-100 for optimal results",
#         example=50
#     )
    
#     batch_size: int = Field(
#         default=32, 
#         ge=8, 
#         le=128, 
#         description="Batch size (8-128). Larger = faster but more memory. Recommended: 32",
#         example=32
#     )
    
#     learning_rate: float = Field(
#         default=0.001, 
#         ge=0.0001, 
#         le=0.01, 
#         description="Learning rate (0.0001-0.01). Lower = more stable. Recommended: 0.001",
#         example=0.001
#     )
    
#     dropout_rate: float = Field(
#         default=0.3,
#         ge=0.0,
#         le=0.7,
#         description="Dropout rate (0.0-0.7) for regularization. Prevents overfitting. Recommended: 0.3",
#         example=0.3
#     )
    
#     hidden_dim: int = Field(
#         default=128,
#         ge=64,
#         le=512,
#         description="Hidden dimension size (64-512). Larger = more capacity. Recommended: 128",
#         example=128
#     )
    
#     use_attention: bool = Field(
#         default=True,
#         description="Use attention mechanism for better feature focus. Recommended: True",
#         example=True
#     )

#     @validator('epochs')
#     def validate_epochs(cls, v):
#         if not 10 <= v <= 300:
#             raise ValueError('Epochs must be between 10 and 300')
#         return v

#     @validator('batch_size')
#     def validate_batch_size(cls, v):
#         if not 8 <= v <= 128:
#             raise ValueError('Batch size must be between 8 and 128')
#         return v

# # ==================== GAN TRAINING SCHEMAS ====================
# class GANTrainingRequest(BaseModel):
#     """
#     Request for GAN model training (Synthetic Data Generation).
#     This trains GANs that generate realistic synthetic patient data.
#     Recommended: 100-200 epochs (trains in 10-30 minutes).
#     """
#     model_config = ConfigDict(
#         protected_namespaces=(),
#         json_schema_extra={
#             "example": {
#                 "epochs": 100,
#                 "batch_size": 32,
#                 "learning_rate": 0.0001,
#                 "lambda_gp": 10.0,
#                 "n_critic": 5,
#                 "latent_dim": 100,
#                 "beta1": 0.5,
#                 "beta2": 0.9
#             }
#         }
#     )
    
#     epochs: int = Field(
#         default=100, 
#         ge=50, 
#         le=500, 
#         description="Training epochs (50-500). More epochs = better quality. Recommended: 100-200",
#         example=100
#     )
    
#     batch_size: int = Field(
#         default=32, 
#         ge=16, 
#         le=128, 
#         description="Batch size (16-128). Larger = faster training. Recommended: 32",
#         example=32
#     )
    
#     learning_rate: float = Field(
#         default=0.0001,
#         ge=0.00001,
#         le=0.001,
#         description="Learning rate (0.00001-0.001). GANs need lower LR. Recommended: 0.0001",
#         example=0.0001
#     )
    
#     lambda_gp: float = Field(
#         default=10.0,
#         ge=1.0,
#         le=50.0,
#         description="Gradient penalty coefficient (1.0-50.0) for WGAN-GP. Controls Lipschitz constraint. Recommended: 10.0",
#         example=10.0
#     )
    
#     n_critic: int = Field(
#         default=5,
#         ge=1,
#         le=10,
#         description="Critic updates per generator update (1-10). More = stable training. Recommended: 5",
#         example=5
#     )
    
#     latent_dim: int = Field(
#         default=100,
#         ge=50,
#         le=512,
#         description="Latent noise dimension (50-512). Higher = more variety. Recommended: 100",
#         example=100
#     )
    
#     beta1: float = Field(
#         default=0.5,
#         ge=0.0,
#         le=0.9,
#         description="Adam optimizer beta1 (0.0-0.9). Lower = less momentum. Recommended: 0.5 for GANs",
#         example=0.5
#     )
    
#     beta2: float = Field(
#         default=0.9,
#         ge=0.9,
#         le=0.999,
#         description="Adam optimizer beta2 (0.9-0.999). Controls variance. Recommended: 0.9",
#         example=0.9
#     )

#     @validator('epochs')
#     def validate_epochs(cls, v):
#         if not 50 <= v <= 500:
#             raise ValueError('Epochs must be between 50 and 500')
#         return v

#     @validator('batch_size')
#     def validate_batch_size(cls, v):
#         if not 16 <= v <= 128:
#             raise ValueError('Batch size must be between 16 and 128')
#         return v

# # ==================== DATA GENERATION SCHEMAS ====================
# class DataGenerationRequest(BaseModel):
#     """Request for synthetic diabetes data generation."""
#     model_config = ConfigDict(
#         json_schema_extra={
#             "example": {
#                 "num_samples": 500,
#                 "diabetes_ratio": 0.5,
#                 "hypertension_ratio": 0.7,
#                 "use_gan": True,
#                 "temperature": 1.0
#             }
#         }
#     )
    
#     num_samples: int = Field(
#         default=100, 
#         ge=1, 
#         le=10000,
#         description="Number of synthetic patients to generate (1-10,000)",
#         example=500
#     )
    
#     diabetes_ratio: float = Field(
#         default=0.5, 
#         ge=0.0, 
#         le=1.0, 
#         description="Ratio of diabetic patients (0.0-1.0). 0.5 = 50% diabetic",
#         example=0.5
#     )
    
#     hypertension_ratio: float = Field(
#         default=0.7, 
#         ge=0.0, 
#         le=1.0, 
#         description="Ratio of hypertensive patients (0.0-1.0). 0.7 = 70% hypertensive",
#         example=0.7
#     )
    
#     use_gan: bool = Field(
#         default=True,
#         description="Use GAN for generation if available, else statistical fallback",
#         example=True
#     )
    
#     temperature: float = Field(
#         default=1.0,
#         ge=0.5,
#         le=2.0,
#         description="Generation temperature (0.5-2.0). Higher = more diversity. Recommended: 1.0",
#         example=1.0
#     )

#     @validator('num_samples')
#     def validate_num_samples(cls, v):
#         if not 1 <= v <= 10000:
#             raise ValueError('Number of samples must be between 1 and 10,000')
#         return v

# # ==================== RESPONSE SCHEMAS ====================
# class TrainingResponse(BaseModel):
#     """Response after supervised model training completion."""
#     model_config = ConfigDict(protected_namespaces=())
    
#     status: str = Field(..., description="Training status", example="success")
#     message: str = Field(..., description="Training completion message", example="Model training completed successfully")
#     epochs_completed: int = Field(..., description="Number of epochs completed", example=50)
#     final_accuracy: float = Field(..., description="Final overall accuracy", example=0.9821)
#     diabetes_accuracy: float = Field(..., description="Diabetes prediction accuracy", example=1.0000)
#     bp_accuracy: float = Field(..., description="Blood pressure prediction accuracy", example=0.9643)
#     training_metrics: Optional[Dict[str, List[float]]] = Field(None, description="Training history metrics")
#     model_timestamp: Optional[str] = Field(None, description="Model training timestamp", example="2025-11-01T13:48:55.456000")

# class GANTrainingResponse(BaseModel):
#     """Response after GAN training completion."""
#     status: str = Field(..., description="Training status", example="success")
#     message: str = Field(..., description="Training completion message")
#     epochs_completed: int = Field(..., description="Number of epochs completed")
#     training_metrics: Optional[Dict[str, List[float]]] = Field(None, description="GAN training history")
#     model_timestamp: Optional[str] = Field(None, description="Model training timestamp")

# class GenerationResponse(BaseModel):
#     """Response after synthetic data generation."""
#     status: str = Field(..., description="Generation status", example="success")
#     message: str = Field(..., description="Generation completion message", example="Successfully generated 1000 synthetic samples")
#     num_generated: int = Field(..., description="Number of samples generated", example=1000)
#     timeseries_file: str = Field(..., description="Path to generated time series CSV file")
#     tabular_file: str = Field(..., description="Path to generated tabular CSV file")
#     preview: Dict[str, Any] = Field(..., description="Preview of generated data including sample records")

# class ValidationResponse(BaseModel):
#     """Response from comprehensive dataset validation."""
#     model_config = ConfigDict(
#         json_schema_extra={
#             "example": {
#                 "status": "success",
#                 "statistical_metrics": {
#                     "completeness": 0.9995,
#                     "consistency": 1.0000,
#                     "accuracy": 0.9823,
#                     "distribution_normality": 0.8571,
#                     "outlier_percentage": 0.0234,
#                     "correlation_validity": 0.6234
#                 },
#                 "utility_metrics": {
#                     "feature_coverage": 1.0000,
#                     "target_balance": 0.7857,
#                     "temporal_consistency": 1.0000,
#                     "clinical_validity": 0.9987,
#                     "data_diversity": 0.8923
#                 },
#                 "quality_score": 0.9523
#             }
#         }
#     )
    
#     status: str = Field(..., description="Validation status", example="success")
#     statistical_metrics: Dict[str, Any] = Field(..., description="Statistical quality metrics")
#     utility_metrics: Dict[str, Any] = Field(..., description="Data utility metrics")
#     quality_score: float = Field(..., description="Overall quality score (0-1)", example=0.9523)

# class ErrorResponse(BaseModel):
#     """Error response schema for failed requests."""
#     status: str = Field(default="error", description="Error status", example="error")
#     message: str = Field(..., description="Error message", example="Training failed: Invalid dataset format")
#     details: Optional[str] = Field(None, description="Additional error details")
from pydantic import BaseModel, Field, validator, ConfigDict
from typing import Optional, List, Dict, Any
from enum import Enum

# ==================== ENUMS ====================
class DiabetesStatusEnum(str, Enum):
    """Diabetes status classification."""
    non_diabetic = "Non-Diabetic"
    diabetic = "Diabetic"

class BPStatusEnum(str, Enum):
    """Blood pressure status classification."""
    normal = "Normal"
    hypertensive = "Hypertensive"

# ==================== GAN TRAINING SCHEMAS ====================
class GANTrainingRequest(BaseModel):
    """
    Request for GAN model training (Synthetic Data Generation).
    This trains GANs that generate realistic synthetic patient data.
    """
    model_config = ConfigDict(
        protected_namespaces=(),
        json_schema_extra={
            "example": {
                "epochs": 100,
                "batch_size": 32
            }
        }
    )
    
    epochs: int = Field(
        default=100,
        ge=1,
        le=500,
        description="Training epochs (1-500). Recommended: 100-200",
        example=100
    )
    
    batch_size: int = Field(
        default=32,
        ge=8,
        le=128,
        description="Batch size (8-128). Recommended: 32",
        example=32
    )
    
    @validator('epochs')
    def validate_epochs(cls, v):
        if not 1 <= v <= 500:
            raise ValueError('Epochs must be between 1 and 500')
        return v
    
    @validator('batch_size')
    def validate_batch_size(cls, v):
        if not 8 <= v <= 128:
            raise ValueError('Batch size must be between 8 and 128')
        return v

# ==================== DATA GENERATION SCHEMAS ====================
class DataGenerationRequest(BaseModel):
    """Request for synthetic diabetes data generation."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "num_samples": 500,
                "diabetes_ratio": 0.5,
                "hypertension_ratio": 0.7
            }
        }
    )
    
    num_samples: int = Field(
        default=100,
        ge=1,
        le=10000,
        description="Number of synthetic patients to generate (1-10,000)",
        example=500
    )
    
    diabetes_ratio: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Ratio of diabetic patients (0.0-1.0)",
        example=0.5
    )
    
    hypertension_ratio: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Ratio of hypertensive patients (0.0-1.0)",
        example=0.7
    )
    
    @validator('num_samples')
    def validate_num_samples(cls, v):
        if not 1 <= v <= 10000:
            raise ValueError('Number of samples must be between 1 and 10,000')
        return v

# ==================== RESPONSE SCHEMAS ====================
class GANTrainingResponse(BaseModel):
    """Response after GAN training completion."""
    status: str = Field(..., description="Training status", example="success")
    message: str = Field(..., description="Training completion message")
    epochs_completed: int = Field(..., description="Number of epochs completed")
    training_metrics: Optional[Dict[str, List[float]]] = Field(None, description="GAN training history")
    model_timestamp: Optional[str] = Field(None, description="Model training timestamp")

class GenerationResponse(BaseModel):
    """Response after synthetic data generation."""
    status: str = Field(..., description="Generation status", example="success")
    message: str = Field(..., description="Generation completion message")
    num_generated: int = Field(..., description="Number of samples generated")
    timeseries_file: str = Field(..., description="Path to generated time series CSV file")
    tabular_file: str = Field(..., description="Path to generated tabular CSV file")
    preview: Dict[str, Any] = Field(..., description="Preview of generated data")

class ErrorResponse(BaseModel):
    """Error response schema for failed requests."""
    status: str = Field(default="error", description="Error status")
    message: str = Field(..., description="Error message")
    details: Optional[str] = Field(None, description="Additional error details")
