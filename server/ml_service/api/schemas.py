from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class TrainRequest(BaseModel):
    time_series_path: str = Field(..., description="Path to time series CSV file")
    tabular_path: str = Field(..., description="Path to tabular CSV file")
    epochs: int = Field(default=100, ge=1, le=1000, description="Number of training epochs")

class TrainResponse(BaseModel):
    message: str
    timestamp: str
    training_history: Dict[str, List[float]]
    epochs: int

class GenerateRequest(BaseModel):
    num_samples: int = Field(..., ge=1, le=10000, description="Number of samples to generate")
    age: Optional[float] = Field(default=None, ge=0, le=100, description="Patient age")
    gender: Optional[str] = Field(default=None, description="Patient gender (Male/Female)")
    disease: Optional[str] = Field(default=None, description="Disease type")

class GenerateResponse(BaseModel):
    message: str
    num_generated: int
    files: Dict[str, str]
    preview: Dict[str, Any]

class MetricsResponse(BaseModel):
    training_history: Dict[str, List[float]]
    model_info: Dict[str, Any]
    device: str
    is_trained: bool

class HealthResponse(BaseModel):
    status: str
    device: str
    models_loaded: bool
    timestamp: str

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
