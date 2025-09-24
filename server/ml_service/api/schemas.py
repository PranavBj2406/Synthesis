from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from pathlib import Path

# Base dataset folder inside your project
BASE_DATASET_DIR = Path(__file__).resolve().parent.parent / "dataset"

class TrainRequest(BaseModel):
    time_series_path: str = Field(..., description="Path to time series CSV file",
                                  example="cleaned_merged_data.csv")
    tabular_path: str = Field(..., description="Path to tabular CSV file",
                              example="cleaned_tabular_data.csv")
    epochs: int = Field(10, ge=1, description="Number of training epochs", example=10)

    class Config:
        schema_extra = {
            "example": {
                "time_series_path": "cleaned_merged_data.csv",
                "tabular_path":"cleaned_tabular_data.csv",
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
