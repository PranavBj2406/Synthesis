# from pydantic import BaseModel, Field
# from typing import List, Optional, Dict, Any

# class TrainRequest(BaseModel):
#     time_series_path: str = Field(..., description="Path to time series CSV file")
#     tabular_path: str = Field(..., description="Path to tabular CSV file")
#     epochs: int = Field(default=100, ge=1, le=1000, description="Number of training epochs")

# class TrainResponse(BaseModel):
#     message: str
#     timestamp: str
#     training_history: Dict[str, List[float]]
#     epochs: int

# class GenerateRequest(BaseModel):
#     num_samples: int = Field(..., ge=1, le=10000, description="Number of samples to generate")
#     age: Optional[float] = Field(default=None, ge=0, le=100, description="Patient age")
#     gender: Optional[str] = Field(default=None, description="Patient gender (Male/Female)")
#     disease: Optional[str] = Field(default=None, description="Disease type")

# class GenerateResponse(BaseModel):
#     message: str
#     num_generated: int
#     files: Dict[str, str]
#     preview: Dict[str, Any]

# class MetricsResponse(BaseModel):
#     training_history: Dict[str, List[float]]
#     model_info: Dict[str, Any]
#     device: str
#     is_trained: bool

# class HealthResponse(BaseModel):
#     status: str
#     device: str
#     models_loaded: bool
#     timestamp: str

# class ErrorResponse(BaseModel):
#     error: str
#     detail: Optional[str] = None
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List


class TrainRequest(BaseModel):
    time_series_path: str = Field(..., description="Path to time series CSV file",
                                  example=r"C:\Users\Asus\Downloads\syn\cleaned_merged_data.csv")
    tabular_path: str = Field(..., description="Path to tabular CSV file",
                              example=r"C:\Users\Asus\Downloads\syn\physionet_output\cleaned_tabular_data.csv")
    epochs: int = Field(10, ge=1, description="Number of training epochs", example=10)

    class Config:
        schema_extra = {
            "example": {
                "time_series_path": r"C:\Users\Asus\Downloads\syn\cleaned_merged_data.csv",
                "tabular_path": r"C:\Users\Asus\Downloads\syn\physionet_output\cleaned_tabular_data.csv",
                "epochs": 10
            }
        }


class TrainResponse(BaseModel):
    message: str
    timestamp: str
    training_history: Optional[Dict[str, Any]] = Field(default_factory=dict)
    epochs: int


class GenerateRequest(BaseModel):
    num_samples: int = Field(..., ge=1, description="How many synthetic samples to generate", example=44)
    age: Optional[float] = Field(None, ge=0, le=120, description="Optional patient age (years)", example=50)
    gender: Optional[str] = Field(None, description="Optional patient gender; accepted values: 'male'|'female'", example="male")
    disease: Optional[str] = Field(None, description="Optional disease type (will be normalized)", example="diabetes")

    @validator("gender")
    def normalize_gender(cls, v):
        if v is None:
            return v
        s = str(v).strip().lower()
        if s not in ("male", "female"):
            raise ValueError("gender must be 'male' or 'female' (case-insensitive)")
        return s

    @validator("disease")
    def normalize_disease(cls, v):
        if v is None:
            return v
        return str(v).strip().lower()

    class Config:
        schema_extra = {
            "example": {
                "num_samples": 44,
                "age": 50,
                "gender": "male",
                "disease": "diabetes"
            }
        }


class GenerateResponse(BaseModel):
    message: str
    num_generated: int
    files: Dict[str, str] = Field(..., description="Paths to generated files (time_series, tabular)")
    preview: Optional[Any] = Field(None, description="A small preview of generated samples (dict/list)")


class MetricsResponse(BaseModel):
    training_history: Optional[Dict[str, Any]] = Field(default_factory=dict)
    model_info: Dict[str, Any]
    device: str
    is_trained: bool


class HealthResponse(BaseModel):
    status: str
    device: str
    models_loaded: bool
    timestamp: str


# Exported names for `from schemas import *`
__all__ = [
    "TrainRequest", "TrainResponse",
    "GenerateRequest", "GenerateResponse",
    "MetricsResponse", "HealthResponse"
]
