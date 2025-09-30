import os
from pathlib import Path
import logging

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.absolute()

# Model parameters for diabetes prediction
SEQ_LENGTH = 13  # 13 hourly readings (6 AM to 6 PM)
LATENT_DIM = 100
HIDDEN_DIM = 128
BATCH_SIZE = 32
EPOCHS = 100

# Updated features for diabetes prediction - FIXED to include hypertension
FEATURES = ['rbs_value']  # Time series feature - RBS values
TABULAR_FEATURES = ['age', 'bmi', 'average_rbs', 'hba1c', 'hypertension', 'respiratory_rate', 'heart_rate', 'spo2']
COND_FEATURES = ['age', 'bmi', 'hba1c']  # Conditioning features
TARGET_VARIABLES = ['diabetes', 'bp_status']  # What we're predicting

# Dataset paths
DATASETS_DIR = PROJECT_ROOT / "datasets"
DEFAULT_TIME_SERIES_PATH = DATASETS_DIR / "enhanced_diabetes_timeseries_dataset.csv"
DEFAULT_TABULAR_PATH = DATASETS_DIR / "enhanced_diabetes_tabular_dataset.csv"

# Output directories
OUTPUT_DIR = PROJECT_ROOT / "synthetic_data"
MODEL_DIR = PROJECT_ROOT / "trained_models"
LOGS_DIR = PROJECT_ROOT / "logs"

# Create directories if they don't exist
for directory in [DATASETS_DIR, OUTPUT_DIR, MODEL_DIR, LOGS_DIR]:
    directory.mkdir(exist_ok=True)

# Convert paths to strings for backward compatibility
DEFAULT_TIME_SERIES_PATH = str(DEFAULT_TIME_SERIES_PATH)
DEFAULT_TABULAR_PATH = str(DEFAULT_TABULAR_PATH)
OUTPUT_DIR = str(OUTPUT_DIR)
MODEL_DIR = str(MODEL_DIR)
LOGS_DIR = str(LOGS_DIR)

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"{LOGS_DIR}/app.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
