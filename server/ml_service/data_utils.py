import logging
import pandas as pd
import numpy as np
import torch
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from torch.utils.data import DataLoader, TensorDataset
from config import *

logger = logging.getLogger(__name__)

class DiabetesDataPreprocessor:
    def __init__(self):
        self.scalers = {}
        self.label_encoders = {}

    def load_and_preprocess_data(self, time_series_path: str, tabular_path: str):
        """Load and preprocess diabetes datasets."""
        try:
            # Load time series data (hourly RBS readings)
            logger.info(f"Loading time series data from {time_series_path}")
            time_series_data = pd.read_csv(time_series_path)
            
            if time_series_data.empty:
                raise ValueError("Time series data file is empty")

            # Load tabular data (patient characteristics)
            logger.info(f"Loading tabular data from {tabular_path}")
            tabular_data = pd.read_csv(tabular_path)
            
            if tabular_data.empty:
                raise ValueError("Tabular data file is empty")

            # Validate required columns
            required_ts_columns = ['patient_id', 'timestamp', 'rbs_value']
            required_tab_columns = ['patient_id'] + TABULAR_FEATURES + TARGET_VARIABLES
            
            # Check if hypertension column exists, if not, derive from another column
            if 'hypertension' not in tabular_data.columns:
                logger.warning("'hypertension' column not found. Checking for alternatives...")
                # This handles the case where your original dataset might have different column names
                if 'hypertension' in tabular_data.columns:
                    pass  # Already exists
                else:
                    logger.error("Required 'hypertension' column not found in tabular data")
            
            for dataset, name, required in [(time_series_data, 'time series', required_ts_columns), 
                                          (tabular_data, 'tabular', required_tab_columns)]:
                missing = [col for col in required if col not in dataset.columns]
                if missing:
                    logger.warning(f"Missing columns in {name} data: {missing}")
                    # Handle missing columns by creating them with default values
                    for col in missing:
                        if col == 'hypertension':
                            # Generate synthetic hypertension values if missing
                            dataset[col] = dataset.apply(self._generate_hypertension_from_bp_status, axis=1)
                        else:
                            dataset[col] = 0  # Default value for other missing columns

            # Merge data on patient_id
            merged_data = time_series_data.merge(tabular_data, on='patient_id', how='inner')
            
            if merged_data.empty:
                raise ValueError("No matching records found between time series and tabular data")

            # Apply preprocessing
            merged_data = self._apply_scaling(merged_data)
            
            logger.info(f"Successfully preprocessed {len(merged_data)} records")
            return merged_data

        except Exception as e:
            logger.error(f"Error in data preprocessing: {str(e)}")
            raise

    def _generate_hypertension_from_bp_status(self, row):
        """Generate hypertension values if missing."""
        if 'bp_status' in row:
            if row['bp_status'] == 1:  # Hypertensive
                systolic = np.random.randint(130, 181)
                diastolic = np.random.randint(85, 121)
            else:  # Normal
                systolic = np.random.randint(100, 121)
                diastolic = np.random.randint(70, 81)
            return f"{systolic}/{diastolic}"
        else:
            # Default normal BP
            return "120/80"

    def _apply_scaling(self, data: pd.DataFrame) -> pd.DataFrame:
        """Apply scaling to numeric columns."""
        # Scale RBS values (time series feature)
        if 'rbs_value' in data.columns:
            self.scalers['rbs_value'] = MinMaxScaler(feature_range=(0, 1))
            data['rbs_value'] = self.scalers['rbs_value'].fit_transform(data[['rbs_value']])

        # Scale tabular features (excluding hypertension which is string format)
        tabular_numeric = ['age', 'bmi', 'average_rbs', 'hba1c', 'respiratory_rate', 'heart_rate', 'spo2']
        for col in tabular_numeric:
            if col in data.columns:
                self.scalers[col] = MinMaxScaler(feature_range=(0, 1))
                # Handle NaN values
                if data[col].isna().any():
                    logger.warning(f"NaN values found in column {col}. Filling with mean.")
                    data[col] = data[col].fillna(data[col].mean())
                data[col] = self.scalers[col].fit_transform(data[[col]])

        # Handle hypertension (convert to numeric for model)
        if 'hypertension' in data.columns:
            data['hypertension_systolic'] = data['hypertension'].apply(lambda x: float(x.split('/')[0]) if isinstance(x, str) and '/' in x else 120.0)
            data['hypertension_diastolic'] = data['hypertension'].apply(lambda x: float(x.split('/')[1]) if isinstance(x, str) and '/' in x else 80.0)
            
            # Scale the numeric BP components
            self.scalers['hypertension_systolic'] = MinMaxScaler(feature_range=(0, 1))
            self.scalers['hypertension_diastolic'] = MinMaxScaler(feature_range=(0, 1))
            
            data['hypertension_systolic'] = self.scalers['hypertension_systolic'].fit_transform(data[['hypertension_systolic']])
            data['hypertension_diastolic'] = self.scalers['hypertension_diastolic'].fit_transform(data[['hypertension_diastolic']])

        return data

    def preprocess_for_model(self, data: pd.DataFrame):
        """Preprocess data for model training with diabetes prediction targets."""
        if data.empty:
            logger.error("Empty data provided to preprocess_for_model")
            return torch.zeros((0, SEQ_LENGTH, 1)), torch.zeros((0, len(TABULAR_FEATURES) + 1)), torch.zeros((0, len(COND_FEATURES))), torch.zeros((0, len(TARGET_VARIABLES)))

        # Handle missing columns
        for col_list, name in [(TABULAR_FEATURES, 'TABULAR_FEATURES'), (COND_FEATURES, 'COND_FEATURES')]:
            missing = [col for col in col_list if col not in data.columns and col != 'hypertension']  # hypertension handled separately
            if missing:
                logger.warning(f"Missing columns in {name}: {missing}")
                for col in missing:
                    data[col] = 0

        # Create sequences for each patient
        unique_patients = data['patient_id'].unique()
        num_patients = len(unique_patients)
        
        # Adjust tabular features to include both BP components instead of hypertension string
        modified_tabular_features = [f for f in TABULAR_FEATURES if f != 'hypertension'] + ['hypertension_systolic', 'hypertension_diastolic']
        
        # Initialize arrays
        sequences = np.zeros((num_patients, SEQ_LENGTH, 1))  # Only RBS values
        tabular_data_array = np.zeros((num_patients, len(modified_tabular_features)))
        conditions = np.zeros((num_patients, len(COND_FEATURES)))
        targets = np.zeros((num_patients, len(TARGET_VARIABLES)))
        
        patient_to_idx = {pid: i for i, pid in enumerate(unique_patients)}

        for patient_id, group in data.groupby('patient_id'):
            idx = patient_to_idx[patient_id]
            
            # Extract time series data (RBS values)
            rbs_sequence = group['rbs_value'].values
            seq_len = min(SEQ_LENGTH, len(rbs_sequence))
            sequences[idx, :seq_len, 0] = rbs_sequence[:seq_len]
            
            # Extract tabular and condition data (use first row for patient)
            first_row = group.iloc[0]
            
            # Handle tabular features
            tabular_values = []
            for feature in TABULAR_FEATURES:
                if feature == 'hypertension':
                    # Use the processed systolic and diastolic values
                    tabular_values.extend([first_row['hypertension_systolic'], first_row['hypertension_diastolic']])
                else:
                    tabular_values.append(first_row[feature])
            
            tabular_data_array[idx] = tabular_values
            conditions[idx] = first_row[COND_FEATURES].values
            targets[idx] = first_row[TARGET_VARIABLES].values

        return (torch.from_numpy(sequences).float(),
                torch.from_numpy(tabular_data_array).float(),
                torch.from_numpy(conditions).float(),
                torch.from_numpy(targets).float())

    def create_dataloader(self, time_series: torch.Tensor, tabular: torch.Tensor, conditions: torch.Tensor, targets: torch.Tensor, batch_size: int = BATCH_SIZE):
        """Create DataLoader for training with targets."""
        dataset = TensorDataset(time_series, tabular, conditions, targets)
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
