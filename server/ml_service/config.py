# import os
# from pathlib import Path

# # Model parameters
# SEQ_LENGTH = 24
# LATENT_DIM = 100
# HIDDEN_DIM = 128
# BATCH_SIZE = 32
# EPOCHS = 100

# # Features
# FEATURES = ['HR', 'Temp', 'RespRate', 'DiasABP', 'Glucose', 'BUN', 'Creatinine', 'WBC', 'HCT', 'GCS']
# TABULAR_FEATURES = ['Age', 'Gender', 'Height', 'Weight', 'ICUType', 'Outcome']
# COND_FEATURES = ['Age', 'Gender', 'disease_label']

# # Default paths
# DEFAULT_TIME_SERIES_PATH = r"C:\Users\Asus\Downloads\syn\cleaned_merged_data.csv"
# DEFAULT_TABULAR_PATH = r"C:\Users\Asus\Downloads\syn\physionet_output\cleaned_tabular_data.csv"

# # Output directories
# OUTPUT_DIR = "synthetic_data"
# MODEL_DIR = "trained_models"
# LOGS_DIR = "logs"

# # Create directories
# for directory in [OUTPUT_DIR, MODEL_DIR, LOGS_DIR]:
#     Path(directory).mkdir(exist_ok=True)
import os
from pathlib import Path
import logging

# Get the project root directory (where this config.py file is located)
PROJECT_ROOT = Path(__file__).parent.absolute()

# Model parameters
SEQ_LENGTH = 24
LATENT_DIM = 100
HIDDEN_DIM = 128
BATCH_SIZE = 32
EPOCHS = 100

# Features
FEATURES = ['HR', 'Temp', 'RespRate', 'DiasABP', 'Glucose', 'BUN', 'Creatinine', 'WBC', 'HCT', 'GCS']
TABULAR_FEATURES = ['Age', 'Gender', 'Height', 'Weight', 'ICUType', 'Outcome']
COND_FEATURES = ['Age', 'Gender', 'disease_label']

# Dataset paths - now using relative paths from project root
DATASETS_DIR = PROJECT_ROOT / "datasets"
DEFAULT_TIME_SERIES_PATH = DATASETS_DIR / "cleaned_merged_data.csv"
DEFAULT_TABULAR_PATH = DATASETS_DIR / "cleaned_tabular_data.csv"

# Output directories - relative to project root
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
