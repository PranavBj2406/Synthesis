import os
import logging
import numpy as np
import pandas as pd
import torch
from datetime import datetime
from typing import Optional, Tuple, Dict, Any
from model_registry import model_registry
from config import *

logger = logging.getLogger(__name__)

class DataGenerator:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
    def generate_synthetic_data(self, num_samples: int, conditions: Optional[torch.Tensor] = None) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Generate synthetic healthcare data."""
        if num_samples <= 0:
            raise ValueError("Number of samples must be positive")
            
        logger.info(f"Generating {num_samples} synthetic samples")
        
        # Get trained models
        ts_generator, tab_generator, _ = model_registry.get_generators()
        
        # Set models to eval mode
        ts_generator.eval()
        tab_generator.eval()
        
        # Generate conditions if not provided
        if conditions is None:
            conditions = self._generate_random_conditions(num_samples)
        else:
            self._validate_conditions(conditions, num_samples)
            
        conditions = conditions.to(self.device)
        
        # Generate synthetic data in batches
        synthetic_ts, synthetic_tab = self._generate_in_batches(
            ts_generator, tab_generator, num_samples, conditions
        )
        
        logger.info("Synthetic data generation completed")
        return synthetic_ts, synthetic_tab, conditions.cpu().numpy()
        
    def _generate_random_conditions(self, num_samples: int) -> torch.Tensor:
        """Generate random conditions."""
        conditions = torch.zeros(num_samples, len(COND_FEATURES))
        
        # Age (normalized to 0-1 range)
        conditions[:, 0] = torch.rand(num_samples) * 0.9 + 0.05
        # Gender (binary)
        conditions[:, 1] = torch.randint(0, 2, (num_samples,)).float()
        # Disease label (categorical)
        conditions[:, 2] = torch.randint(0, 5, (num_samples,)).float()
        
        return conditions
        
    def _validate_conditions(self, conditions: torch.Tensor, num_samples: int):
        """Validate provided conditions."""
        if not isinstance(conditions, torch.Tensor):
            raise TypeError("Conditions must be a PyTorch tensor")
        if conditions.shape[0] != num_samples:
            raise ValueError(f"Expected {num_samples} conditions, got {conditions.shape[0]}")
        if conditions.shape[1] != len(COND_FEATURES):
            raise ValueError(f"Expected {len(COND_FEATURES)} condition features, got {conditions.shape[1]}")
            
    def _generate_in_batches(self, ts_generator, tab_generator, num_samples: int, conditions: torch.Tensor) -> Tuple[np.ndarray, np.ndarray]:
        """Generate data in batches to avoid memory issues."""
        batch_size = min(32, num_samples)
        num_batches = (num_samples + batch_size - 1) // batch_size
        
        synthetic_ts_list = []
        synthetic_tab_list = []
        
        with torch.no_grad():
            for i in range(num_batches):
                start_idx = i * batch_size
                end_idx = min((i + 1) * batch_size, num_samples)
                
                # Generate latent vectors
                z = torch.randn(end_idx - start_idx, LATENT_DIM, device=self.device)
                batch_cond = conditions[start_idx:end_idx]
                
                # Generate synthetic data
                batch_ts = ts_generator(z, batch_cond)
                batch_tab = tab_generator(z, batch_cond)
                
                synthetic_ts_list.append(batch_ts.cpu())
                synthetic_tab_list.append(batch_tab.cpu())
                
        # Concatenate batches
        synthetic_ts = torch.cat(synthetic_ts_list, dim=0).numpy()
        synthetic_tab = torch.cat(synthetic_tab_list, dim=0).numpy()
        
        return synthetic_ts, synthetic_tab
        
    def save_synthetic_data(self, synthetic_ts: np.ndarray, synthetic_tab: np.ndarray, 
                           conditions: np.ndarray, scalers: Dict, label_encoders: Dict, 
                           num_samples: int) -> Tuple[str, str]:
        """Save generated synthetic data to CSV files."""
        # Create output directory
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        # Generate timestamp for filenames
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Process and save data
        ts_data = self._process_time_series_data(synthetic_ts, scalers)
        tab_data = self._process_tabular_data(synthetic_tab, conditions, scalers, label_encoders)
        
        # Create DataFrames
        ts_df = pd.DataFrame(ts_data)
        tab_df = pd.DataFrame(tab_data)
        
        # Define file paths
        ts_file = os.path.join(OUTPUT_DIR, f"synthetic_timeseries_{timestamp}_{num_samples}.csv")
        tab_file = os.path.join(OUTPUT_DIR, f"synthetic_tabular_{timestamp}_{num_samples}.csv")
        
        # Save to CSV
        ts_df.to_csv(ts_file, index=False)
        tab_df.to_csv(tab_file, index=False)
        
        logger.info(f"Synthetic data saved to {ts_file} and {tab_file}")
        return ts_file, tab_file
        
    def _process_time_series_data(self, synthetic_ts: np.ndarray, scalers: Dict) -> list:
        """Process time series data for saving."""
        ts_data = []
        
        for i in range(synthetic_ts.shape[0]):
            for j in range(synthetic_ts.shape[1]):
                record = {
                    'RecordID': i + 1,
                    'TimeStep': j
                }
                
                # Process each feature
                for k, feature in enumerate(FEATURES):
                    try:
                        if feature in scalers and scalers[feature] is not None:
                            val = np.clip(synthetic_ts[i, j, k], 0, 1)
                            record[feature] = scalers[feature].inverse_transform([[val]])[0][0]
                        else:
                            record[feature] = synthetic_ts[i, j, k]
                    except Exception as e:
                        logger.warning(f"Error processing feature {feature}: {str(e)}")
                        record[feature] = synthetic_ts[i, j, k]
                        
                ts_data.append(record)
                
        return ts_data
        
    def _process_tabular_data(self, synthetic_tab: np.ndarray, conditions: np.ndarray, 
                             scalers: Dict, label_encoders: Dict) -> list:
        """Process tabular data for saving."""
        tab_data = []
        
        for i in range(synthetic_tab.shape[0]):
            record = {'RecordID': i + 1}
            
            # Process tabular features
            for j, feature in enumerate(TABULAR_FEATURES):
                try:
                    if feature in scalers and scalers[feature] is not None:
                        val = np.clip(synthetic_tab[i, j], 0, 1)
                        record[feature] = scalers[feature].inverse_transform([[val]])[0][0]
                    elif feature in label_encoders and label_encoders[feature] is not None:
                        num_classes = len(label_encoders[feature].classes_)
                        value = int(round(synthetic_tab[i, j] * (num_classes - 1)))
                        value = max(0, min(value, num_classes - 1))
                        record[feature] = label_encoders[feature].inverse_transform([value])[0]
                    else:
                        record[feature] = synthetic_tab[i, j]
                except Exception as e:
                    logger.warning(f"Error processing tabular feature {feature}: {str(e)}")
                    record[feature] = synthetic_tab[i, j]
                    
            # Process condition features
            for j, feature in enumerate(COND_FEATURES):
                try:
                    if feature in scalers and scalers[feature] is not None:
                        val = np.clip(conditions[i, j], 0, 1)
                        record[feature] = scalers[feature].inverse_transform([[val]])[0][0]
                    elif feature in label_encoders and feature != 'disease_label' and label_encoders[feature] is not None:
                        value = int(round(conditions[i, j]))
                        num_classes = len(label_encoders[feature].classes_)
                        value = max(0, min(value, num_classes - 1))
                        record[feature] = label_encoders[feature].inverse_transform([value])[0]
                    elif feature == 'disease_label':
                        record[feature] = int(round(conditions[i, j]))
                    else:
                        record[feature] = conditions[i, j]
                except Exception as e:
                    logger.warning(f"Error processing condition feature {feature}: {str(e)}")
                    record[feature] = conditions[i, j]
                    
            tab_data.append(record)
            
        return tab_data
        
    def create_sample_preview(self, synthetic_ts: np.ndarray, synthetic_tab: np.ndarray, 
                             conditions: np.ndarray, num_samples: int = 3) -> Dict[str, Any]:
        """Create a preview of generated data for API response."""
        preview = {
            'num_generated': synthetic_ts.shape[0],
            'time_series_shape': list(synthetic_ts.shape),
            'tabular_shape': list(synthetic_tab.shape),
            'conditions_shape': list(conditions.shape),
            'samples': []
        }
        
        # Add sample data
        for i in range(min(num_samples, synthetic_ts.shape[0])):
            sample = {
                'record_id': i + 1,
                'time_series': synthetic_ts[i].tolist(),
                'tabular': synthetic_tab[i].tolist(),
                'conditions': conditions[i].tolist()
            }
            preview['samples'].append(sample)
            
        return preview
