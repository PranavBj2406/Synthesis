import logging
import pandas as pd
import numpy as np
import torch
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from torch.utils.data import DataLoader, TensorDataset
from config import *

logger = logging.getLogger(__name__)

class DataPreprocessor:
    def __init__(self):
        self.scalers = {}
        self.label_encoders = {}
    
    def load_and_preprocess_data(self, time_series_path: str, tabular_path: str):
        """Load and preprocess time series and tabular data."""
        try:
            # Load time series data
            logger.info(f"Loading time series data from {time_series_path}")
            time_series_data = pd.read_csv(time_series_path)
            if time_series_data.empty:
                raise ValueError("Time series data file is empty")
            
            # Load tabular data
            logger.info(f"Loading tabular data from {tabular_path}")
            tabular_data = pd.read_csv(tabular_path)
            if tabular_data.empty:
                raise ValueError("Tabular data file is empty")
            
            # Validate required columns
            required_columns = ['RecordID']
            for dataset, name in [(time_series_data, 'time series'), (tabular_data, 'tabular')]:
                missing = [col for col in required_columns if col not in dataset.columns]
                if missing:
                    raise ValueError(f"Missing required columns in {name} data: {missing}")
            
            # Check for duplicates and missing records
            self._log_data_issues(time_series_data, tabular_data)
            
            # Merge data
            merged_data = time_series_data.merge(tabular_data, on='RecordID', how='inner')
            if merged_data.empty:
                raise ValueError("No matching records found between time series and tabular data")
            
            # Apply preprocessing
            merged_data = self._apply_label_encoding(merged_data)
            merged_data = self._apply_scaling(merged_data)
            
            logger.info(f"Successfully preprocessed {len(merged_data)} records")
            return merged_data
            
        except Exception as e:
            logger.error(f"Error in data preprocessing: {str(e)}")
            raise
    
    def _log_data_issues(self, time_series_data: pd.DataFrame, tabular_data: pd.DataFrame):
        """Log data quality issues."""
        # Check for duplicate RecordIDs
        tabular_counts = tabular_data['RecordID'].value_counts()
        duplicates = tabular_counts[tabular_counts > 1]
        if not duplicates.empty:
            logger.warning(f"{len(duplicates)} RecordIDs in tabular data have multiple rows")
        
        # Log missing RecordIDs
        missing_in_tabular = set(time_series_data['RecordID']) - set(tabular_data['RecordID'])
        missing_in_time_series = set(tabular_data['RecordID']) - set(time_series_data['RecordID'])
        
        if missing_in_tabular:
            logger.info(f"{len(missing_in_tabular)} RecordIDs in time-series data not found in tabular data")
        
        if missing_in_time_series:
            logger.info(f"{len(missing_in_time_series)} RecordIDs in tabular data not found in time-series data")
    
    def _apply_label_encoding(self, data: pd.DataFrame) -> pd.DataFrame:
        """Apply label encoding to categorical columns."""
        categorical_columns = ['disease_label', 'Gender', 'ICUType', 'Outcome']
        
        for col in categorical_columns:
            if col in data.columns:
                self.label_encoders[col] = LabelEncoder()
                data[col] = self.label_encoders[col].fit_transform(data[col].astype(str))
        
        return data
    
    def _apply_scaling(self, data: pd.DataFrame) -> pd.DataFrame:
        """Apply scaling to numeric columns."""
        numeric_columns = FEATURES + ['Age', 'Height', 'Weight']
        
        for col in numeric_columns:
            if col in data.columns:
                self.scalers[col] = MinMaxScaler()
                # Handle NaN values
                if data[col].isna().any():
                    logger.warning(f"NaN values found in column {col}. Filling with mean.")
                    data[col] = data[col].fillna(data[col].mean())
                
                data[col] = self.scalers[col].fit_transform(data[[col]])
        
        return data
    
    def preprocess_for_model(self, data: pd.DataFrame):
        """Preprocess data for model training."""
        if data.empty:
            logger.error("Empty data provided to preprocess_for_model")
            return torch.zeros((0, SEQ_LENGTH, len(FEATURES))), torch.zeros((0, len(TABULAR_FEATURES))), torch.zeros((0, len(COND_FEATURES)))
        
        # Handle missing columns
        for col_list, name in [(FEATURES, 'FEATURES'), (TABULAR_FEATURES, 'TABULAR_FEATURES'), (COND_FEATURES, 'COND_FEATURES')]:
            missing = [col for col in col_list if col not in data.columns]
            if missing:
                logger.warning(f"Missing columns in {name}: {missing}")
                for col in missing:
                    data[col] = 0
        
        # Create sequences efficiently
        unique_records = data['RecordID'].unique()
        num_records = len(unique_records)
        
        sequences = np.zeros((num_records, SEQ_LENGTH, len(FEATURES)))
        tabular_data = np.zeros((num_records, len(TABULAR_FEATURES)))
        conds = np.zeros((num_records, len(COND_FEATURES)))
        
        record_to_idx = {rid: i for i, rid in enumerate(unique_records)}
        
        for rid, group in data.groupby('RecordID'):
            idx = record_to_idx[rid]
            
            # Extract time series data
            seq = group[FEATURES].values
            seq_len = min(SEQ_LENGTH, len(seq))
            sequences[idx, :seq_len] = seq[:seq_len]
            
            # Extract tabular and condition data
            first_row = group.iloc[0]
            tabular_data[idx] = first_row[TABULAR_FEATURES].values
            conds[idx] = first_row[COND_FEATURES].values
        
        return (torch.from_numpy(sequences).float(),
                torch.from_numpy(tabular_data).float(),
                torch.from_numpy(conds).float())
    
    def create_dataloader(self, time_series: torch.Tensor, tabular: torch.Tensor, conditions: torch.Tensor, batch_size: int = BATCH_SIZE):
        """Create DataLoader for training."""
        dataset = TensorDataset(time_series, tabular, conditions)
        effective_batch_size = min(batch_size, len(dataset))
        
        if effective_batch_size < batch_size:
            logger.warning(f"Dataset size ({len(dataset)}) smaller than batch size ({batch_size}). Using {effective_batch_size}")
        
        return DataLoader(
            dataset,
            batch_size=effective_batch_size,
            shuffle=True,
            drop_last=False,
            num_workers=0,
            pin_memory=True
        )
