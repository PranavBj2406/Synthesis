
# from pydantic import BaseModel, Field, validator
# from typing import Optional, Dict, Any, List


# class TrainRequest(BaseModel):
#     time_series_path: str = Field(..., description="Path to time series CSV file",
#                                   example=r"C:\Users\Asus\Downloads\syn\cleaned_merged_data.csv")
#     tabular_path: str = Field(..., description="Path to tabular CSV file",
#                               example=r"C:\Users\Asus\Downloads\syn\physionet_output\cleaned_tabular_data.csv")
#     epochs: int = Field(10, ge=1, description="Number of training epochs", example=10)

#     class Config:
#         schema_extra = {
#             "example": {
#                 "time_series_path": r"C:\Users\Asus\Downloads\syn\cleaned_merged_data.csv",
#                 "tabular_path": r"C:\Users\Asus\Downloads\syn\physionet_output\cleaned_tabular_data.csv",
#                 "epochs": 10
#             }
#         }


# class TrainResponse(BaseModel):
#     message: str
#     timestamp: str
#     training_history: Optional[Dict[str, Any]] = Field(default_factory=dict)
#     epochs: int


# class GenerateRequest(BaseModel):
#     num_samples: int = Field(..., ge=1, description="How many synthetic samples to generate", example=44)
#     age: Optional[float] = Field(None, ge=0, le=120, description="Optional patient age (years)", example=50)
#     gender: Optional[str] = Field(None, description="Optional patient gender; accepted values: 'male'|'female'", example="male")
#     disease: Optional[str] = Field(None, description="Optional disease type (will be normalized)", example="diabetes")

#     @validator("gender")
#     def normalize_gender(cls, v):
#         if v is None:
#             return v
#         s = str(v).strip().lower()
#         if s not in ("male", "female"):
#             raise ValueError("gender must be 'male' or 'female' (case-insensitive)")
#         return s

#     @validator("disease")
#     def normalize_disease(cls, v):
#         if v is None:
#             return v
#         return str(v).strip().lower()

#     class Config:
#         schema_extra = {
#             "example": {
#                 "num_samples": 44,
#                 "age": 50,
#                 "gender": "male",
#                 "disease": "diabetes"
#             }
#         }


# class GenerateResponse(BaseModel):
#     message: str
#     num_generated: int
#     files: Dict[str, str] = Field(..., description="Paths to generated files (time_series, tabular)")
#     preview: Optional[Any] = Field(None, description="A small preview of generated samples (dict/list)")


# class MetricsResponse(BaseModel):
#     training_history: Optional[Dict[str, Any]] = Field(default_factory=dict)
#     model_info: Dict[str, Any]
#     device: str
#     is_trained: bool


# class HealthResponse(BaseModel):
#     status: str
#     device: str
#     models_loaded: bool
#     timestamp: str


# # Exported names for `from schemas import *`
# __all__ = [
#     "TrainRequest", "TrainResponse",
#     "GenerateRequest", "GenerateResponse",
#     "MetricsResponse", "HealthResponse"
# ]
from pydantic import BaseModel, Field, validator, ConfigDict
from typing import Optional, List, Dict, Any
from enum import Enum

class GenderEnum(str, Enum):
    male = "Male"
    female = "Female"

class DiseaseTypeEnum(str, Enum):
    diabetes = "Diabetes"
    heart_disease = "Heart Disease"
    respiratory = "Respiratory"
    neurological = "Neurological"
    other = "Other"

# Training request schema matching Streamlit parameters
class TrainingRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())  # Fix for model_timestamp warning
    
    epochs: int = Field(default=100, ge=10, le=300, description="Number of training epochs")
    batch_size: int = Field(default=32, ge=8, le=128, description="Training batch size")
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

# Data generation request schema matching Streamlit parameters
class DataGenerationRequest(BaseModel):
    age: int = Field(default=40, ge=18, le=90, description="Patient age")
    gender: GenderEnum = Field(default=GenderEnum.male, description="Patient gender")
    disease_type: DiseaseTypeEnum = Field(default=DiseaseTypeEnum.diabetes, description="Disease type")
    num_records: int = Field(default=10, ge=1, le=1000, description="Number of records to generate")

    @validator('age')
    def validate_age(cls, v):
        if not 18 <= v <= 90:
            raise ValueError('Age must be between 18 and 90')
        return v

    @validator('num_records')
    def validate_num_records(cls, v):
        if not 1 <= v <= 1000:
            raise ValueError('Number of records must be between 1 and 1000')
        return v

# Response schemas
class TrainingResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())  # Fix for model_timestamp warning
    
    status: str
    message: str
    epochs_completed: int
    training_metrics: Optional[Dict[str, List[float]]]
    model_timestamp: Optional[str]

class GenerationResponse(BaseModel):
    status: str
    message: str
    num_generated: int
    time_series_file: str
    tabular_file: str
    preview: Dict[str, Any]

class ValidationResponse(BaseModel):
    status: str
    statistical_metrics: Dict[str, Any]
    utility_metrics: Dict[str, Any]
    quality_score: float

class ErrorResponse(BaseModel):
    status: str = "error"
    message: str
    details: Optional[str] = None

