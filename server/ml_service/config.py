import os
from pathlib import Path

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

# Default paths
DEFAULT_TIME_SERIES_PATH = r"C:\Users\Asus\Downloads\syn\cleaned_merged_data.csv"
DEFAULT_TABULAR_PATH = r"C:\Users\Asus\Downloads\syn\physionet_output\cleaned_tabular_data.csv"

# Output directories
OUTPUT_DIR = "synthetic_data"
MODEL_DIR = "trained_models"
LOGS_DIR = "logs"

# Create directories
for directory in [OUTPUT_DIR, MODEL_DIR, LOGS_DIR]:
    Path(directory).mkdir(exist_ok=True)
