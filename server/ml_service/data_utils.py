
# import logging
# import pandas as pd
# import numpy as np
# import torch
# from sklearn.preprocessing import MinMaxScaler, LabelEncoder
# from torch.utils.data import DataLoader, TensorDataset
# from config import *
# import requests
# from io import StringIO
# import warnings

# logger = logging.getLogger(__name__)

# class DiabetesDataPreprocessor:
#     def __init__(self):
#         self.scalers = {}
#         self.label_encoders = {}

#     def load_and_preprocess_data(self, time_series_path: str, tabular_path: str):
#         """Load and preprocess diabetes datasets from local or URL."""
#         try:
#             # Load time series data (supports both local paths and URLs)
#             logger.info(f"Loading time series data from {time_series_path}")
#             time_series_data = self._load_csv(time_series_path)
            
#             if time_series_data.empty:
#                 raise ValueError("Time series data file is empty")

#             logger.info(f"✓ Time series data loaded: {time_series_data.shape}")

#             # Load tabular data (supports both local paths and URLs)
#             logger.info(f"Loading tabular data from {tabular_path}")
#             tabular_data = self._load_csv(tabular_path)
            
#             if tabular_data.empty:
#                 raise ValueError("Tabular data file is empty")

#             logger.info(f"✓ Tabular data loaded: {tabular_data.shape}")

#             # Validate required columns
#             required_ts_columns = ['patient_id', 'timestamp', 'rbs_value']
#             required_tab_columns = ['patient_id'] + [f for f in TABULAR_FEATURES if f != 'hypertension'] + TARGET_VARIABLES
            
#             # Check time series columns
#             missing_ts = [col for col in required_ts_columns if col not in time_series_data.columns]
#             if missing_ts:
#                 raise ValueError(f"Missing required columns in time series data: {missing_ts}")
            
#             # Check tabular columns
#             missing_tab = [col for col in required_tab_columns if col not in tabular_data.columns]
            
#             # Handle missing hypertension column
#             if 'hypertension' not in tabular_data.columns:
#                 logger.warning("'hypertension' column not found. Generating from bp_status...")
#                 tabular_data['hypertension'] = tabular_data.apply(self._generate_hypertension_from_bp_status, axis=1)
            
#             if missing_tab:
#                 logger.warning(f"Missing columns in tabular data: {missing_tab}")
#                 for col in missing_tab:
#                     tabular_data[col] = 0

#             # Merge data on patient_id
#             logger.info("Merging time series and tabular data...")
#             merged_data = time_series_data.merge(tabular_data, on='patient_id', how='inner')
            
#             if merged_data.empty:
#                 raise ValueError("No matching records found between time series and tabular data")

#             logger.info(f"✓ Merged data shape: {merged_data.shape}")

#             # Apply preprocessing
#             merged_data = self._apply_scaling(merged_data)
            
#             logger.info(f"✓ Successfully preprocessed {len(merged_data)} records")
#             logger.info(f"✓ Unique patients: {merged_data['patient_id'].nunique()}")
#             return merged_data

#         except Exception as e:
#             logger.error(f"✗ Error in data preprocessing: {str(e)}")
#             raise

#     def _load_csv(self, path: str) -> pd.DataFrame:
#         """Load CSV from local file or URL."""
#         try:
#             if path.startswith('http://') or path.startswith('https://'):
#                 # Load from URL
#                 logger.info(f"Fetching data from URL...")
#                 response = requests.get(path, timeout=30)
#                 response.raise_for_status()
#                 return pd.read_csv(StringIO(response.text))
#             else:
#                 # Load from local file
#                 return pd.read_csv(path)
#         except requests.exceptions.RequestException as e:
#             logger.error(f"Failed to fetch data from URL: {str(e)}")
#             raise ValueError(f"Failed to load data from {path}: {str(e)}")
#         except Exception as e:
#             logger.error(f"Failed to load CSV: {str(e)}")
#             raise

#     def _generate_hypertension_from_bp_status(self, row):
#         """Generate hypertension values if missing."""
#         if 'bp_status' in row:
#             if row['bp_status'] == 1:  # Hypertensive
#                 systolic = np.random.randint(130, 181)
#                 diastolic = np.random.randint(85, 121)
#             else:  # Normal
#                 systolic = np.random.randint(100, 121)
#                 diastolic = np.random.randint(70, 81)
#             return f"{systolic}/{diastolic}"
#         else:
#             return "120/80"

#     def _apply_scaling(self, data: pd.DataFrame) -> pd.DataFrame:
#         """Apply scaling to numeric columns."""
#         # Scale RBS values (time series feature)
#         if 'rbs_value' in data.columns:
#             self.scalers['rbs_value'] = MinMaxScaler(feature_range=(0, 1))
#             data['rbs_value'] = self.scalers['rbs_value'].fit_transform(data[['rbs_value']])

#         # Scale tabular features (excluding hypertension which is string format)
#         tabular_numeric = ['age', 'bmi', 'average_rbs', 'hba1c', 'respiratory_rate', 'heart_rate', 'spo2']
#         for col in tabular_numeric:
#             if col in data.columns:
#                 self.scalers[col] = MinMaxScaler(feature_range=(0, 1))
#                 # Handle NaN values
#                 if data[col].isna().any():
#                     logger.warning(f"NaN values found in column {col}. Filling with mean.")
#                     data[col] = data[col].fillna(data[col].mean())
#                 data[col] = self.scalers[col].fit_transform(data[[col]])

#         # Handle hypertension (convert to numeric for model)
#         if 'hypertension' in data.columns:
#             data['hypertension_systolic'] = data['hypertension'].apply(
#                 lambda x: float(str(x).split('/')[0]) if isinstance(x, str) and '/' in str(x) else 120.0
#             )
#             data['hypertension_diastolic'] = data['hypertension'].apply(
#                 lambda x: float(str(x).split('/')[1]) if isinstance(x, str) and '/' in str(x) else 80.0
#             )
            
#             # Scale the numeric BP components
#             self.scalers['hypertension_systolic'] = MinMaxScaler(feature_range=(0, 1))
#             self.scalers['hypertension_diastolic'] = MinMaxScaler(feature_range=(0, 1))
            
#             data['hypertension_systolic'] = self.scalers['hypertension_systolic'].fit_transform(data[['hypertension_systolic']])
#             data['hypertension_diastolic'] = self.scalers['hypertension_diastolic'].fit_transform(data[['hypertension_diastolic']])

#         return data

#     def preprocess_for_model(self, data: pd.DataFrame):
#         """Preprocess data for model training with diabetes prediction targets."""
#         if data.empty:
#             logger.error("Empty data provided to preprocess_for_model")
#             return torch.zeros((0, SEQ_LENGTH, 1)), torch.zeros((0, 9)), torch.zeros((0, len(COND_FEATURES))), torch.zeros((0, len(TARGET_VARIABLES)))

#         # Handle missing columns
#         for col_list, name in [(TABULAR_FEATURES, 'TABULAR_FEATURES'), (COND_FEATURES, 'COND_FEATURES')]:
#             missing = [col for col in col_list if col not in data.columns and col != 'hypertension']
#             if missing:
#                 logger.warning(f"Missing columns in {name}: {missing}")
#                 for col in missing:
#                     data[col] = 0

#         # Create sequences for each patient
#         unique_patients = data['patient_id'].unique()
#         num_patients = len(unique_patients)
        
#         # Adjust tabular features to include both BP components instead of hypertension string
#         modified_tabular_features = [f for f in TABULAR_FEATURES if f != 'hypertension'] + ['hypertension_systolic', 'hypertension_diastolic']
        
#         # Initialize arrays
#         sequences = np.zeros((num_patients, SEQ_LENGTH, 1))  # Only RBS values
#         tabular_data_array = np.zeros((num_patients, len(modified_tabular_features)))
#         conditions = np.zeros((num_patients, len(COND_FEATURES)))
#         targets = np.zeros((num_patients, len(TARGET_VARIABLES)))
        
#         patient_to_idx = {pid: i for i, pid in enumerate(unique_patients)}

#         for patient_id, group in data.groupby('patient_id'):
#             idx = patient_to_idx[patient_id]
            
#             # Extract time series data (RBS values)
#             rbs_sequence = group['rbs_value'].values
#             seq_len = min(SEQ_LENGTH, len(rbs_sequence))
#             sequences[idx, :seq_len, 0] = rbs_sequence[:seq_len]
            
#             # Extract tabular and condition data (use first row for patient)
#             first_row = group.iloc[0]
            
#             # Handle tabular features
#             tabular_values = []
#             for feature in TABULAR_FEATURES:
#                 if feature == 'hypertension':
#                     # Use the processed systolic and diastolic values
#                     tabular_values.extend([first_row['hypertension_systolic'], first_row['hypertension_diastolic']])
#                 else:
#                     tabular_values.append(first_row[feature])
            
#             tabular_data_array[idx] = tabular_values
#             conditions[idx] = first_row[COND_FEATURES].values
#             targets[idx] = first_row[TARGET_VARIABLES].values

#         logger.info(f"✓ Prepared {num_patients} patient sequences")

#         return (torch.from_numpy(sequences).float(),
#                 torch.from_numpy(tabular_data_array).float(),
#                 torch.from_numpy(conditions).float(),
#                 torch.from_numpy(targets).float())

#     def create_dataloader(self, time_series: torch.Tensor, tabular: torch.Tensor, conditions: torch.Tensor, targets: torch.Tensor, batch_size: int = BATCH_SIZE):
#         """Create DataLoader for training with targets."""
#         dataset = TensorDataset(time_series, tabular, conditions, targets)
#         effective_batch_size = min(batch_size, len(dataset))
        
#         if effective_batch_size < batch_size:
#             logger.warning(f"Dataset size ({len(dataset)}) smaller than batch size ({batch_size}). Using {effective_batch_size}")

#         # Suppress pin_memory warnings by setting it to False when no GPU
#         use_pin_memory = torch.cuda.is_available()

#         return DataLoader(
#             dataset,
#             batch_size=effective_batch_size,
#             shuffle=True,
#             drop_last=False,
#             num_workers=0,
#             pin_memory=use_pin_memory  # Only use pin_memory with GPU
#         )

import logging
import pandas as pd
import numpy as np
import torch
from sklearn.preprocessing import MinMaxScaler
from torch.utils.data import DataLoader, TensorDataset
from config import *
import requests
from io import StringIO

logger = logging.getLogger(__name__)

class DiabetesDataPreprocessor:
    def __init__(self):
        self.scalers = {}
        self.label_encoders = {}

    def load_and_preprocess_data(self, time_series_path: str, tabular_path: str):
        """Load and preprocess diabetes datasets from GitHub URLs ONLY."""
        try:
            # Load time series data (GITHUB ONLY - NO LOCAL FALLBACK)
            logger.info(f"Loading time series data from GitHub: {time_series_path}")
            time_series_data = self._load_csv(time_series_path)
            if time_series_data.empty:
                raise ValueError("Time series data file is empty")
            logger.info(f"[OK] Time series data loaded: {time_series_data.shape[0]} rows, {time_series_data.shape[1]} columns")

            # Load tabular data (GITHUB ONLY - NO LOCAL FALLBACK)
            logger.info(f"Loading tabular data from GitHub: {tabular_path}")
            tabular_data = self._load_csv(tabular_path)
            if tabular_data.empty:
                raise ValueError("Tabular data file is empty")
            logger.info(f"[OK] Tabular data loaded: {tabular_data.shape[0]} rows, {tabular_data.shape[1]} columns")

            # Validate required columns
            required_ts_columns = ['patient_id', 'timestamp', 'rbs_value']
            required_tab_columns = ['patient_id'] + [f for f in TABULAR_FEATURES if f != 'hypertension'] + TARGET_VARIABLES

            # Check time series columns
            missing_ts = [col for col in required_ts_columns if col not in time_series_data.columns]
            if missing_ts:
                raise ValueError(f"Missing required columns in time series data: {missing_ts}")

            # Check tabular columns
            missing_tab = [col for col in required_tab_columns if col not in tabular_data.columns]
            
            # Handle missing hypertension column
            if 'hypertension' not in tabular_data.columns:
                logger.warning("'hypertension' column not found. Generating from bp_status...")
                tabular_data['hypertension'] = tabular_data.apply(self._generate_hypertension_from_bp_status, axis=1)

            if missing_tab:
                raise ValueError(f"Missing required columns in tabular data: {missing_tab}")

            # Merge data on patient_id
            logger.info("Merging time series and tabular data...")
            merged_data = time_series_data.merge(tabular_data, on='patient_id', how='inner')
            
            if merged_data.empty:
                raise ValueError("No matching patient IDs between time series and tabular data. Verify dataset consistency on GitHub.")

            logger.info(f"[OK] Merged data shape: {merged_data.shape}")

            # Apply preprocessing
            merged_data = self._apply_scaling(merged_data)

            logger.info(f"[OK] Successfully preprocessed {len(merged_data)} records")
            logger.info(f"[OK] Unique patients: {merged_data['patient_id'].nunique()}")

            return merged_data

        except Exception as e:
            logger.error(f"[ERROR] Error in data preprocessing: {str(e)}")
            raise

    def _load_csv(self, path: str) -> pd.DataFrame:
        """Load CSV from GitHub URL ONLY - NO LOCAL FALLBACK."""
        try:
            if not (path.startswith('http://') or path.startswith('https://')):
                raise RuntimeError(f"Only GitHub URLs are supported. Invalid path: {path}")

            # Fetch from GitHub
            logger.info(f"Fetching dataset from GitHub...")
            response = requests.get(path, timeout=30)
            response.raise_for_status()  # Raise HTTPError for bad status codes
            
            logger.info(f"[OK] HTTP {response.status_code}: Dataset fetched successfully")
            return pd.read_csv(StringIO(response.text))

        except requests.exceptions.HTTPError as e:
            error_msg = f"Failed to load dataset from GitHub. URL: {path}, HTTP Status: {e.response.status_code}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error while fetching dataset from GitHub. URL: {path}, Error: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error loading CSV from GitHub. URL: {path}, Error: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e

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
            data['hypertension_systolic'] = data['hypertension'].apply(
                lambda x: float(str(x).split('/')[0]) if isinstance(x, str) and '/' in str(x) else 120.0
            )
            data['hypertension_diastolic'] = data['hypertension'].apply(
                lambda x: float(str(x).split('/')[1]) if isinstance(x, str) and '/' in str(x) else 80.0
            )

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
            return torch.zeros((0, SEQ_LENGTH, 1)), torch.zeros((0, 9)), torch.zeros((0, len(COND_FEATURES))), torch.zeros((0, len(TARGET_VARIABLES)))

        # Handle missing columns
        for col_list, name in [(TABULAR_FEATURES, 'TABULAR_FEATURES'), (COND_FEATURES, 'COND_FEATURES')]:
            missing = [col for col in col_list if col not in data.columns and col != 'hypertension']
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

        logger.info(f"[OK] Prepared {num_patients} patient sequences")

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

        use_pin_memory = torch.cuda.is_available()

        return DataLoader(
            dataset,
            batch_size=effective_batch_size,
            shuffle=True,
            drop_last=False,
            num_workers=0,
            pin_memory=use_pin_memory
        )
