from pydantic import BaseModel, Field, validator, ConfigDict
from typing import Optional, List, Dict, Any
from enum import Enum

class DiabetesStatusEnum(str, Enum):
    non_diabetic = "Non-Diabetic"
    diabetic = "Diabetic"

class BPStatusEnum(str, Enum):
    normal = "Normal"
    hypertensive = "Hypertensive"

class DiabetesPredictionRequest(BaseModel):
    """Request for diabetes and BP prediction."""
    age: int = Field(..., ge=30, le=55, description="Patient age")
    bmi: float = Field(..., ge=18.5, le=45.0, description="Body Mass Index")
    average_rbs: float = Field(..., ge=100.0, le=400.0, description="Average RBS level")
    hba1c: float = Field(..., ge=5.72, le=7.0, description="HbA1c percentage")
    respiratory_rate: int = Field(..., ge=12, le=18, description="Respiratory rate")
    heart_rate: int = Field(..., ge=70, le=100, description="Heart rate")
    spo2: float = Field(..., ge=95.0, le=100.0, description="SpO2 percentage")
    rbs_sequence: List[float] = Field(..., description="Hourly RBS readings (13 values)")

    @validator('rbs_sequence')
    def validate_rbs_sequence(cls, v):
        if len(v) != 13:
            raise ValueError('RBS sequence must contain exactly 13 hourly readings')
        if not all(100.0 <= val <= 400.0 for val in v):
            raise ValueError('All RBS values must be between 100.0 and 400.0')
        return v

class DiabetesPredictionResponse(BaseModel):
    """Response for diabetes and BP prediction."""
    diabetes_probability: float = Field(..., description="Probability of diabetes (0-1)")
    diabetes_prediction: DiabetesStatusEnum = Field(..., description="Diabetes prediction")
    bp_probability: float = Field(..., description="Probability of hypertension (0-1)")
    bp_prediction: BPStatusEnum = Field(..., description="Blood pressure prediction")
    confidence_score: float = Field(..., description="Overall prediction confidence")

class TrainingRequest(BaseModel):
    """Request for model training."""
    model_config = ConfigDict(protected_namespaces=())
    
    epochs: int = Field(default=100, ge=10, le=300, description="Number of training epochs")
    batch_size: int = Field(default=32, ge=8, le=128, description="Training batch size")
    learning_rate: float = Field(default=0.001, ge=0.0001, le=0.01, description="Learning rate")
    time_series_path: Optional[str] = Field(default=None, description="Custom time series dataset path")
    tabular_path: Optional[str] = Field(default=None, description="Custom tabular dataset path")

    @validator('epochs')
    def validate_epochs(cls, v):
        if not 10 <= v <= 300:
            raise ValueError('Epochs must be between 10 and 300')
        return v

    @validator('batch_size')
    def validate_batch_size(cls, v):
        if not 8 <= v <= 128:
            raise ValueError('Batch size must be between 8 and 128')
        return v

class DataGenerationRequest(BaseModel):
    """Request for synthetic data generation."""
    num_samples: int = Field(default=100, ge=1, le=1000, description="Number of samples to generate")
    diabetes_ratio: float = Field(default=0.5, ge=0.0, le=1.0, description="Ratio of diabetic samples")
    hypertension_ratio: float = Field(default=0.7, ge=0.0, le=1.0, description="Ratio of hypertensive samples")

    @validator('num_samples')
    def validate_num_samples(cls, v):
        if not 1 <= v <= 1000:
            raise ValueError('Number of samples must be between 1 and 1000')
        return v

class TrainingResponse(BaseModel):
    """Response for training."""
    model_config = ConfigDict(protected_namespaces=())
    
    status: str
    message: str
    epochs_completed: int
    final_accuracy: float
    diabetes_accuracy: float
    bp_accuracy: float
    training_metrics: Optional[Dict[str, List[float]]] = None
    model_timestamp: Optional[str] = None

class GenerationResponse(BaseModel):
    """Response for data generation."""
    status: str
    message: str
    num_generated: int
    timeseries_file: str
    tabular_file: str
    preview: Dict[str, Any]

class ValidationResponse(BaseModel):
    """Response for validation."""
    status: str
    statistical_metrics: Dict[str, Any]
    utility_metrics: Dict[str, Any]
    quality_score: float

class ErrorResponse(BaseModel):
    """Error response schema."""
    status: str = "error"
    message: str
    details: Optional[str] = None
