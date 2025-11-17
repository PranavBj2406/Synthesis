
# import os
# import logging
# import numpy as np
# import pandas as pd
# import torch
# from datetime import datetime
# from typing import Dict, Any

# from gan_trainer import GANTrainer
# from config import OUTPUT_DIR, SEQ_LENGTH, LATENT_DIM, TABULAR_FEATURES, COND_FEATURES

# logger = logging.getLogger(__name__)

# class DiabetesDataGenerator:
#     """GAN-based generator for synthetic diabetes data."""
    
#     def __init__(self):
#         self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
#         self.gan_trainer = GANTrainer()
        
#         # Try to load pretrained models
#         self.models_loaded = self.gan_trainer.load_models()
        
#         if self.models_loaded:
#             logger.info("✓ Using pretrained GAN models for generation")
#         else:
#             logger.warning("⚠ GAN models not found. Will use statistical generation as fallback.")

#     def generate_synthetic_data(self, num_samples: int, diabetes_ratio: float = 0.5,
#                                 hypertension_ratio: float = 0.7) -> Dict[str, Any]:
#         """Generate synthetic diabetes data using GAN or statistical fallback."""
#         logger.info(f"Generating {num_samples} synthetic diabetes samples...")
        
#         if self.models_loaded:
#             # Use GAN models
#             tabular_data, timeseries_data = self._generate_with_gan(
#                 num_samples, diabetes_ratio, hypertension_ratio
#             )
#         else:
#             # Fallback to statistical generation
#             logger.warning("Using statistical fallback for data generation")
#             tabular_data = self._generate_tabular_data_statistical(
#                 num_samples, diabetes_ratio, hypertension_ratio
#             )
#             timeseries_data = self._generate_timeseries_data_statistical(tabular_data)
        
#         # Save to CSV files
#         ts_file, tab_file = self._save_to_csv(timeseries_data, tabular_data, num_samples)
        
#         # Create preview
#         preview = self._create_preview(timeseries_data, tabular_data)
        
#         return {
#             'timeseries_file': ts_file,
#             'tabular_file': tab_file,
#             'preview': preview
#         }

#     def _generate_with_gan(self, num_samples: int, diabetes_ratio: float,
#                           hypertension_ratio: float) -> tuple:
#         """Generate data using trained GAN models - FIXED DENORMALIZATION."""
#         logger.info("Generating data with GAN models...")
        
#         self.gan_trainer.tab_gen.eval()
#         self.gan_trainer.ts_gen.eval()
#         self.gan_trainer.cross_modal.eval()
        
#         all_tabular_data = []
#         all_timeseries_data = []
        
#         with torch.no_grad():
#             # Generate in batches
#             batch_size = 100
#             num_batches = (num_samples + batch_size - 1) // batch_size
            
#             for batch_idx in range(num_batches):
#                 current_batch_size = min(batch_size, num_samples - batch_idx * batch_size)
                
#                 # Generate condition features
#                 conditions = self._generate_conditions(current_batch_size, diabetes_ratio)
#                 conditions_tensor = torch.FloatTensor(conditions).to(self.device)
                
#                 # Generate latent noise
#                 z = torch.randn(current_batch_size, LATENT_DIM, device=self.device)
                
#                 # Generate tabular data
#                 fake_tabular = self.gan_trainer.tab_gen(z, conditions_tensor)
                
#                 # Generate time series data
#                 fake_timeseries = self.gan_trainer.ts_gen(z, conditions_tensor)
                
#                 # Convert to numpy and denormalize
#                 fake_tabular_np = fake_tabular.cpu().numpy()
#                 fake_timeseries_np = fake_timeseries.cpu().numpy()
                
#                 # Process each sample
#                 for i in range(current_batch_size):
#                     patient_id = f'P{batch_idx * batch_size + i + 1:05d}'
                    
#                     # Denormalize tabular data - FIXED
#                     tab_sample = self._denormalize_tabular(fake_tabular_np[i], conditions[i])
#                     tab_sample['patient_id'] = patient_id
                    
#                     # Determine diabetes outcome based on medical rules
#                     if tab_sample['average_rbs'] > 200 and tab_sample['hba1c'] > 6.5:
#                         tab_sample['diabetes'] = 1
#                     elif tab_sample['average_rbs'] < 140 and tab_sample['hba1c'] < 5.7:
#                         tab_sample['diabetes'] = 0
#                     else:
#                         # Borderline cases
#                         tab_sample['diabetes'] = 1 if np.random.random() < diabetes_ratio else 0
                    
#                     # Determine BP status based on hypertension value
#                     systolic, diastolic = map(int, tab_sample['hypertension'].split('/'))
#                     if systolic > 120 or diastolic > 80:
#                         tab_sample['bp_status'] = 1
#                     else:
#                         tab_sample['bp_status'] = 0
                    
#                     all_tabular_data.append(tab_sample)
                    
#                     # Denormalize time series data
#                     ts_samples = self._denormalize_timeseries(
#                         fake_timeseries_np[i], patient_id, tab_sample['average_rbs']
#                     )
#                     all_timeseries_data.extend(ts_samples)
        
#         tabular_df = pd.DataFrame(all_tabular_data)
#         timeseries_df = pd.DataFrame(all_timeseries_data)
        
#         logger.info(f"✓ Generated {len(tabular_df)} patients using GAN")
#         logger.info(f"✓ Diabetes distribution: {tabular_df['diabetes'].value_counts().to_dict()}")
#         logger.info(f"✓ BP status distribution: {tabular_df['bp_status'].value_counts().to_dict()}")
        
#         return tabular_df, timeseries_df

#     def _generate_conditions(self, num_samples: int, diabetes_ratio: float):
#         """Generate condition features for conditional GAN."""
#         conditions = []
#         for _ in range(num_samples):
#             is_diabetic = np.random.random() < diabetes_ratio
            
#             if is_diabetic:
#                 age = np.random.uniform(0.7, 1.0)  # 38-55 years normalized
#                 bmi = np.random.uniform(0.6, 0.9)  # Higher BMI
#                 hba1c = np.random.uniform(0.9, 1.0)  # 6.3-7.0%
#             else:
#                 age = np.random.uniform(0.5, 0.7)  # 30-38 years
#                 bmi = np.random.uniform(0.4, 0.6)  # Lower BMI
#                 hba1c = np.random.uniform(0.8, 0.87)  # 5.72-6.1%
            
#             conditions.append([age, bmi, hba1c])
        
#         return conditions

#     def _denormalize_tabular(self, normalized_data, condition):
#         """Denormalize tabular data from [0,1] to real ranges - FIXED."""
#         # Extract condition features (already used for GAN conditioning)
#         age = int(condition[0] * 55.0)  # 0-55 range
#         age = max(30, min(55, age))  # Clip to valid range
        
#         bmi = condition[1] * 45.0
#         bmi = max(18.5, min(45.0, bmi))
        
#         hba1c = condition[2] * 7.0
#         hba1c = max(5.72, min(7.0, hba1c))
        
#         # FIXED: Correct feature mapping (normalized_data has 9 values)
#         # Output from TabularGenerator: [avg_rbs, rr, hr, spo2, systolic, diastolic, remaining...]
#         try:
#             # Denormalize generated features
#             average_rbs = normalized_data[0] * 300.0 + 100.0  # 100-400 range
#             respiratory_rate = int(normalized_data[1] * 6 + 12)  # 12-18 range
#             heart_rate = int(normalized_data[2] * 30 + 70)  # 70-100 range
#             spo2 = normalized_data[3] * 5.0 + 95.0  # 95-100 range
            
#             # BP values
#             systolic = int(normalized_data[4] * 80 + 100)  # 100-180 range
#             diastolic = int(normalized_data[5] * 50 + 70)  # 70-120 range
            
#             # Ensure clinical validity
#             average_rbs = max(100.0, min(400.0, average_rbs))
#             respiratory_rate = max(12, min(18, respiratory_rate))
#             heart_rate = max(70, min(100, heart_rate))
#             spo2 = max(95.0, min(100.0, spo2))
#             systolic = max(100, min(180, systolic))
#             diastolic = max(70, min(120, diastolic))
            
#             # Ensure diastolic is reasonable relative to systolic
#             if diastolic > systolic - 20:
#                 diastolic = max(70, systolic - 20)
            
#             hypertension = f"{systolic}/{diastolic}"
            
#             return {
#                 'age': age,
#                 'bmi': round(float(bmi), 1),
#                 'average_rbs': round(float(average_rbs), 1),
#                 'hba1c': round(float(hba1c), 2),
#                 'hypertension': hypertension,
#                 'respiratory_rate': respiratory_rate,
#                 'heart_rate': heart_rate,
#                 'spo2': round(float(spo2), 1)
#             }
#         except IndexError as e:
#             logger.error(f"Denormalization error: {e}. Data shape: {normalized_data.shape}")
#             # Return default values
#             return {
#                 'age': age,
#                 'bmi': round(float(bmi), 1),
#                 'average_rbs': 150.0,
#                 'hba1c': round(float(hba1c), 2),
#                 'hypertension': "120/80",
#                 'respiratory_rate': 15,
#                 'heart_rate': 80,
#                 'spo2': 98.0
#             }

#     def _denormalize_timeseries(self, normalized_sequence, patient_id, avg_rbs):
#         """Denormalize time series data."""
#         base_date = datetime.now().date()
#         timeseries_samples = []
        
#         for hour_offset in range(min(SEQ_LENGTH, len(normalized_sequence))):
#             current_hour = 6 + hour_offset
#             timestamp = datetime.combine(base_date, datetime.min.time().replace(hour=current_hour))
            
#             # Denormalize RBS value
#             rbs_value = float(normalized_sequence[hour_offset][0]) * 300.0 + 100.0
            
#             # Add medical correlation with average RBS
#             rbs_value = rbs_value * 0.6 + avg_rbs * 0.4
#             rbs_value = max(100.0, min(400.0, rbs_value))
            
#             timeseries_samples.append({
#                 'patient_id': patient_id,
#                 'timestamp': timestamp,
#                 'rbs_value': round(rbs_value, 1)
#             })
        
#         return timeseries_samples

#     def _generate_tabular_data_statistical(self, num_samples: int, diabetes_ratio: float,
#                                           hypertension_ratio: float) -> pd.DataFrame:
#         """Statistical fallback for tabular data generation."""
#         data = []
        
#         for i in range(num_samples):
#             is_diabetic = np.random.random() < diabetes_ratio
            
#             if is_diabetic:
#                 age = np.random.randint(45, 56)
#                 bmi = np.clip(np.random.normal(29.0, 4.0), 18.5, 45.0)
#                 average_rbs = np.clip(np.random.normal(280, 50), 100.0, 400.0)
#                 hba1c = np.clip(np.random.normal(6.8, 0.3), 5.72, 7.0)
#                 hr = np.random.randint(78, 95)
#             else:
#                 age = np.random.randint(30, 45)
#                 bmi = np.clip(np.random.normal(24.0, 3.0), 18.5, 45.0)
#                 average_rbs = np.clip(np.random.normal(140, 25), 100.0, 400.0)
#                 hba1c = np.clip(np.random.normal(5.8, 0.2), 5.72, 7.0)
#                 hr = np.random.randint(70, 85)
            
#             rr = np.random.randint(12, 19)
#             spo2 = np.random.uniform(95.0, 100.0)
            
#             is_hypertensive = np.random.random() < hypertension_ratio
            
#             if is_hypertensive or (is_diabetic and np.random.random() < 0.8):
#                 systolic = np.random.randint(130, 181)
#                 diastolic = np.random.randint(85, 121)
#                 bp_status = 1
#             else:
#                 systolic = np.random.randint(100, 121)
#                 diastolic = np.random.randint(70, 81)
#                 bp_status = 0
            
#             if diastolic > systolic - 20:
#                 diastolic = max(70, systolic - 20)
            
#             hypertension = f"{systolic}/{diastolic}"
            
#             data.append({
#                 'patient_id': f'P{i+1:05d}',
#                 'age': age,
#                 'bmi': round(bmi, 1),
#                 'average_rbs': round(average_rbs, 1),
#                 'hba1c': round(hba1c, 2),
#                 'hypertension': hypertension,
#                 'respiratory_rate': rr,
#                 'heart_rate': hr,
#                 'spo2': round(spo2, 1),
#                 'diabetes': 1 if is_diabetic else 0,
#                 'bp_status': bp_status
#             })
        
#         return pd.DataFrame(data)

#     def _generate_timeseries_data_statistical(self, tabular_df: pd.DataFrame) -> pd.DataFrame:
#         """Statistical fallback for time series generation."""
#         timeseries_data = []
#         base_date = datetime.now().date()
        
#         for _, patient in tabular_df.iterrows():
#             avg_rbs = patient['average_rbs']
#             is_diabetic = patient['diabetes'] == 1
            
#             for hour_offset in range(SEQ_LENGTH):
#                 current_hour = 6 + hour_offset
#                 timestamp = datetime.combine(base_date, datetime.min.time().replace(hour=current_hour))
                
#                 # Diurnal variation
#                 if hour_offset <= 2:
#                     rbs_multiplier = np.random.normal(1.05, 0.1)
#                 elif hour_offset in [3, 4]:
#                     rbs_multiplier = np.random.normal(1.25, 0.15)
#                 elif hour_offset in [6, 7]:
#                     rbs_multiplier = np.random.normal(1.20, 0.12)
#                 elif hour_offset in [8, 9]:
#                     rbs_multiplier = np.random.normal(1.10, 0.10)
#                 else:
#                     rbs_multiplier = np.random.normal(0.95, 0.08)
                
#                 rbs_value = avg_rbs * rbs_multiplier
#                 rbs_value += np.random.normal(0, 15 if is_diabetic else 10)
#                 rbs_value = max(100.0, min(400.0, rbs_value))
                
#                 timeseries_data.append({
#                     'patient_id': patient['patient_id'],
#                     'timestamp': timestamp,
#                     'rbs_value': round(rbs_value, 1)
#                 })
        
#         return pd.DataFrame(timeseries_data)

#     def _save_to_csv(self, timeseries_df: pd.DataFrame, tabular_df: pd.DataFrame,
#                      num_samples: int) -> tuple:
#         """Save data to CSV files."""
#         os.makedirs(OUTPUT_DIR, exist_ok=True)
        
#         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#         generation_method = "GAN" if self.models_loaded else "Statistical"
        
#         ts_file = os.path.join(OUTPUT_DIR, f"synthetic_timeseries_{generation_method}_{timestamp}_{num_samples}.csv")
#         tab_file = os.path.join(OUTPUT_DIR, f"synthetic_tabular_{generation_method}_{timestamp}_{num_samples}.csv")
        
#         timeseries_df.to_csv(ts_file, index=False)
#         tabular_df.to_csv(tab_file, index=False)
        
#         logger.info(f"✓ Synthetic data saved using {generation_method} method")
#         logger.info(f"✓ Files: {ts_file}, {tab_file}")
        
#         return ts_file, tab_file

#     def _create_preview(self, timeseries_df: pd.DataFrame, tabular_df: pd.DataFrame) -> Dict[str, Any]:
#         """Create a preview of generated data."""
#         preview = {
#             'generation_method': 'GAN' if self.models_loaded else 'Statistical',
#             'num_generated': len(tabular_df),
#             'timeseries_shape': list(timeseries_df.shape),
#             'tabular_shape': list(tabular_df.shape),
#             'tabular_columns': list(tabular_df.columns),
#             'sample_hypertension_values': tabular_df['hypertension'].head(5).tolist(),
#             'sample_patients': []
#         }
        
#         for i in range(min(3, len(tabular_df))):
#             patient_id = tabular_df.iloc[i]['patient_id']
#             patient_ts = timeseries_df[timeseries_df['patient_id'] == patient_id]
            
#             sample = {
#                 'patient_id': patient_id,
#                 'tabular_data': tabular_df.iloc[i].to_dict(),
#                 'timeseries_sample': patient_ts.head(5).to_dict('records')
#             }
#             preview['sample_patients'].append(sample)
        
#         return preview
# import os
import logging
import numpy as np
import pandas as pd
import torch
from datetime import datetime
from typing import Dict, Any
import os
from gan_trainer import GANTrainer
from config import OUTPUT_DIR, SEQ_LENGTH, LATENT_DIM

logger = logging.getLogger(__name__)

class DiabetesDataGenerator:
    """GAN-based generator for synthetic diabetes data (NO STATISTICAL FALLBACK)."""
    
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.gan_trainer = GANTrainer()
        
        # Try to load pretrained models
        self.models_loaded = self.gan_trainer.load_models()
        
        if self.models_loaded:
            logger.info("[OK] Using pretrained GAN models for generation")
        else:
            logger.warning("[WARNING] GAN models not found. Train models using /api/v1/train/gan first.")

    def generate_synthetic_data(self, num_samples: int, diabetes_ratio: float = 0.5,
                               hypertension_ratio: float = 0.7) -> Dict[str, Any]:
        """Generate synthetic diabetes data using GAN ONLY (no fallback)."""
        logger.info(f"Generating {num_samples} synthetic diabetes samples...")

        if not self.models_loaded:
            raise RuntimeError("GAN models not available. Please train using /api/v1/train/gan first.")

        # Use GAN models
        tabular_data, timeseries_data = self._generate_with_gan(
            num_samples, diabetes_ratio, hypertension_ratio
        )

        # Validate generated data
        is_valid = self.validate_generated_data(tabular_data)
        if not is_valid:
            logger.warning("Generated data contains medical inconsistencies")

        # Save to CSV files
        ts_file, tab_file = self._save_to_csv(timeseries_data, tabular_data, num_samples)

        # Create preview
        preview = self._create_preview(timeseries_data, tabular_data)

        return {
            'timeseries_file': ts_file,
            'tabular_file': tab_file,
            'preview': preview
        }

    def _generate_with_gan(self, num_samples: int, diabetes_ratio: float,
                          hypertension_ratio: float) -> tuple:
        """Generate data using trained GAN models with medical consistency."""
        logger.info("Generating data with GAN models...")
        
        self.gan_trainer.tab_gen.eval()
        self.gan_trainer.ts_gen.eval()
        self.gan_trainer.cross_modal.eval()

        all_tabular_data = []
        all_timeseries_data = []

        with torch.no_grad():
            # Generate in batches
            batch_size = 100
            num_batches = (num_samples + batch_size - 1) // batch_size

            for batch_idx in range(num_batches):
                current_batch_size = min(batch_size, num_samples - batch_idx * batch_size)

                # Generate condition features with medical realism
                conditions = self._generate_conditions(current_batch_size, diabetes_ratio)
                conditions_tensor = torch.FloatTensor(conditions).to(self.device)

                # Generate latent noise
                z = torch.randn(current_batch_size, LATENT_DIM, device=self.device)

                # Generate tabular data
                fake_tabular = self.gan_trainer.tab_gen(z, conditions_tensor)

                # Generate time series data
                fake_timeseries = self.gan_trainer.ts_gen(z, conditions_tensor)

                # Convert to numpy and denormalize
                fake_tabular_np = fake_tabular.cpu().numpy()
                fake_timeseries_np = fake_timeseries.cpu().numpy()

                # Process each sample
                for i in range(current_batch_size):
                    patient_id = f'P{batch_idx * batch_size + i + 1:05d}'

                    # Denormalize tabular data with medical accuracy
                    tab_sample = self._denormalize_tabular(fake_tabular_np[i], conditions[i])
                    tab_sample['patient_id'] = patient_id

                    # === MEDICAL RULE-BASED CLASSIFICATION ===
                    # Diabetes: HbA1c >= 6.5% OR average RBS >= 140
                    if tab_sample['hba1c'] >= 6.5 or tab_sample['average_rbs'] >= 140:
                        tab_sample['diabetes'] = 1
                    else:
                        tab_sample['diabetes'] = 0

                    # BP status: systolic > 130 OR diastolic > 85
                    systolic, diastolic = map(int, tab_sample['hypertension'].split('/'))
                    if systolic > 130 or diastolic > 85:
                        tab_sample['bp_status'] = 1
                    else:
                        tab_sample['bp_status'] = 0

                    all_tabular_data.append(tab_sample)

                    # Denormalize time series data
                    ts_samples = self._denormalize_timeseries(
                        fake_timeseries_np[i], patient_id, tab_sample['average_rbs'],
                        tab_sample['diabetes']
                    )
                    all_timeseries_data.extend(ts_samples)

        tabular_df = pd.DataFrame(all_tabular_data)
        timeseries_df = pd.DataFrame(all_timeseries_data)

        logger.info(f"[OK] Generated {len(tabular_df)} patients using GAN")
        logger.info(f"[OK] Diabetes distribution: {tabular_df['diabetes'].value_counts().to_dict()}")
        logger.info(f"[OK] BP status distribution: {tabular_df['bp_status'].value_counts().to_dict()}")
        
        # Log medical statistics
        diabetic_rbs = tabular_df[tabular_df['diabetes']==1]['average_rbs'].mean()
        non_diabetic_rbs = tabular_df[tabular_df['diabetes']==0]['average_rbs'].mean()
        logger.info(f"[OK] Avg RBS - Diabetic: {diabetic_rbs:.1f}, Non-diabetic: {non_diabetic_rbs:.1f}")

        return tabular_df, timeseries_df

    def _generate_conditions(self, num_samples: int, diabetes_ratio: float):
        """Generate REALISTIC condition features for conditional GAN."""
        conditions = []
        for _ in range(num_samples):
            is_diabetic = np.random.random() < diabetes_ratio

            if is_diabetic:
                # Diabetic patients: higher age, BMI, HbA1c
                age = np.random.uniform(0.6, 1.0)  # 43-55 years (normalized)
                bmi = np.random.uniform(0.65, 0.95)  # 28-40 BMI (normalized)
                hba1c = np.random.uniform(0.85, 1.0)  # 6.5-7.0% HbA1c (normalized)
            else:
                # Non-diabetic: younger, lower BMI and HbA1c
                age = np.random.uniform(0.0, 0.5)  # 30-40 years (normalized)
                bmi = np.random.uniform(0.1, 0.5)  # 20-28 BMI (normalized)
                hba1c = np.random.uniform(0.0, 0.5)  # 5.72-6.0% HbA1c (normalized)

            conditions.append([age, bmi, hba1c])

        return conditions

    def _denormalize_tabular(self, normalized_data, condition):
        """Denormalize with MEDICAL REALISM and proper scaling."""
        # Extract condition features (already normalized [0,1])
        age = int(condition[0] * 25 + 30)  # 30-55 years
        age = max(30, min(55, age))

        bmi = condition[1] * 26.5 + 18.5  # 18.5-45.0
        bmi = max(18.5, min(45.0, bmi))

        hba1c = condition[2] * 1.28 + 5.72  # 5.72-7.0%
        hba1c = max(5.72, min(7.0, hba1c))

        # Determine diabetes probability based on medical criteria
        is_likely_diabetic = (hba1c >= 6.5 or bmi > 30)

        try:
            # === CRITICAL FIX: Realistic RBS ranges ===
            if is_likely_diabetic:
                # Diabetic RBS: 140-280 mg/dL (mostly 160-220)
                base_rbs = np.random.normal(190, 35)  # Mean 190, SD 35
                gan_variation = (normalized_data[0] - 0.5) * 60  # GAN adds ±30
                average_rbs = base_rbs + gan_variation
                average_rbs = max(140.0, min(280.0, average_rbs))
            else:
                # Non-diabetic RBS: 80-125 mg/dL (mostly 90-110)
                base_rbs = np.random.normal(100, 12)  # Mean 100, SD 12
                gan_variation = (normalized_data[0] - 0.5) * 24  # GAN adds ±12
                average_rbs = base_rbs + gan_variation
                average_rbs = max(80.0, min(125.0, average_rbs))

            # Vital signs with realistic variation
            # Respiratory rate: 12-18 breaths/min
            resp_base = 14 + (normalized_data[1] - 0.5) * 6
            respiratory_rate = int(np.clip(resp_base, 12, 18))

            # Heart rate: 60-100 bpm
            hr_base = 75 + (normalized_data[2] - 0.5) * 30
            heart_rate = int(np.clip(hr_base, 60, 100))

            # SpO2: 93-100%
            spo2_base = 97 + (normalized_data[3] - 0.5) * 6
            spo2 = np.clip(spo2_base, 93.0, 100.0)

            # Blood pressure based on diabetes/age with realistic ranges
            if is_likely_diabetic or age > 45:
                # Elevated BP for high-risk patients
                systolic_base = 135 + (normalized_data[4] - 0.5) * 40  # 115-155
                diastolic_base = 85 + (normalized_data[5] - 0.5) * 30   # 70-100
            else:
                # Normal BP for low-risk patients
                systolic_base = 115 + (normalized_data[4] - 0.5) * 30  # 100-130
                diastolic_base = 75 + (normalized_data[5] - 0.5) * 20   # 65-85

            systolic = int(np.clip(systolic_base, 100, 180))
            diastolic = int(np.clip(diastolic_base, 60, 120))

            # Ensure pulse pressure is reasonable (systolic - diastolic = 30-60)
            pulse_pressure = systolic - diastolic
            if pulse_pressure < 25:
                diastolic = max(60, systolic - 35)
            elif pulse_pressure > 70:
                systolic = min(180, diastolic + 55)

            hypertension = f"{systolic}/{diastolic}"

            return {
                'age': age,
                'bmi': round(float(bmi), 1),
                'average_rbs': round(float(average_rbs), 1),
                'hba1c': round(float(hba1c), 2),
                'hypertension': hypertension,
                'respiratory_rate': respiratory_rate,
                'heart_rate': heart_rate,
                'spo2': round(float(spo2), 1)
            }

        except (IndexError, ValueError) as e:
            logger.error(f"Denormalization error: {e}. Data shape: {normalized_data.shape}")
            # Return medically plausible defaults
            return {
                'age': age,
                'bmi': round(float(bmi), 1),
                'average_rbs': 180.0 if is_likely_diabetic else 100.0,
                'hba1c': round(float(hba1c), 2),
                'hypertension': "135/85" if is_likely_diabetic else "115/75",
                'respiratory_rate': 14,
                'heart_rate': 75,
                'spo2': 97.0
            }

    def _denormalize_timeseries(self, normalized_sequence, patient_id, avg_rbs, is_diabetic):
        """Denormalize time series data with realistic RBS fluctuations."""
        base_date = datetime.now().date()
        timeseries_samples = []

        # Determine realistic daily RBS variation range
        if is_diabetic:
            # Diabetic patients have higher variability (±30-50 mg/dL)
            variation_range = 40
        else:
            # Non-diabetic patients have lower variability (±15-25 mg/dL)
            variation_range = 20

        for hour_offset in range(min(SEQ_LENGTH, len(normalized_sequence))):
            current_hour = 6 + hour_offset
            timestamp = datetime.combine(base_date, datetime.min.time().replace(hour=current_hour))

            # Use GAN output to create variation around the patient's average RBS
            gan_deviation = (float(normalized_sequence[hour_offset][0]) - 0.5) * 2  # [-1, 1]
            rbs_variation = gan_deviation * variation_range

            # Add time-of-day effects
            if 6 <= current_hour <= 8:  # Morning fasting
                time_adjustment = -10 if is_diabetic else -5
            elif 11 <= current_hour <= 13:  # Post-lunch peak
                time_adjustment = 20 if is_diabetic else 10
            elif 17 <= current_hour <= 19:  # Post-dinner peak
                time_adjustment = 15 if is_diabetic else 8
            else:
                time_adjustment = 0

            rbs_value = avg_rbs + rbs_variation + time_adjustment

            # Ensure values stay in medically valid range
            if is_diabetic:
                rbs_value = max(110.0, min(320.0, rbs_value))
            else:
                rbs_value = max(70.0, min(140.0, rbs_value))

            timeseries_samples.append({
                'patient_id': patient_id,
                'timestamp': timestamp,
                'rbs_value': round(rbs_value, 1)
            })

        return timeseries_samples

    def validate_generated_data(self, tabular_df: pd.DataFrame) -> bool:
        """Validate medical consistency of generated data."""
        issues = []
        
        # Check RBS consistency with diabetes status
        diabetic_mask = tabular_df['diabetes'] == 1
        non_diabetic_mask = tabular_df['diabetes'] == 0
        
        # Non-diabetics should not have RBS > 125 (allowing 5mg/dL margin)
        non_diabetic_high_rbs = tabular_df[non_diabetic_mask & (tabular_df['average_rbs'] > 130)]
        if len(non_diabetic_high_rbs) > 0:
            issues.append(f"{len(non_diabetic_high_rbs)} non-diabetics with RBS > 130 mg/dL")
        
        # Diabetics should typically have RBS > 135
        diabetic_low_rbs = tabular_df[diabetic_mask & (tabular_df['average_rbs'] < 135)]
        if len(diabetic_low_rbs) > 0:
            issues.append(f"{len(diabetic_low_rbs)} diabetics with RBS < 135 mg/dL")
        
        # Check HbA1c consistency
        diabetic_low_hba1c = tabular_df[diabetic_mask & (tabular_df['hba1c'] < 6.3)]
        if len(diabetic_low_hba1c) > 0:
            issues.append(f"{len(diabetic_low_hba1c)} diabetics with HbA1c < 6.3%")
        
        non_diabetic_high_hba1c = tabular_df[non_diabetic_mask & (tabular_df['hba1c'] > 6.2)]
        if len(non_diabetic_high_hba1c) > 0:
            issues.append(f"{len(non_diabetic_high_hba1c)} non-diabetics with HbA1c > 6.2%")
        
        if issues:
            logger.warning(f"Data quality issues detected: {issues}")
            return False
        
        logger.info("[OK] Generated data passed medical consistency validation")
        return True

    def _save_to_csv(self, timeseries_df: pd.DataFrame, tabular_df: pd.DataFrame,
                    num_samples: int) -> tuple:
        """Save data to CSV files."""
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        ts_file = os.path.join(OUTPUT_DIR, f"synthetic_timeseries_GAN_{timestamp}_{num_samples}.csv")
        tab_file = os.path.join(OUTPUT_DIR, f"synthetic_tabular_GAN_{timestamp}_{num_samples}.csv")

        timeseries_df.to_csv(ts_file, index=False)
        tabular_df.to_csv(tab_file, index=False)

        logger.info(f"[OK] Synthetic data saved using GAN method")
        logger.info(f"[OK] Files: {ts_file}, {tab_file}")

        return ts_file, tab_file

    def _create_preview(self, timeseries_df: pd.DataFrame, tabular_df: pd.DataFrame) -> Dict[str, Any]:
        """Create a preview of generated data with statistics."""
        # Calculate statistics
        diabetic_stats = tabular_df[tabular_df['diabetes'] == 1]['average_rbs'].describe()
        non_diabetic_stats = tabular_df[tabular_df['diabetes'] == 0]['average_rbs'].describe()
        
        preview = {
            'generation_method': 'GAN',
            'num_generated': len(tabular_df),
            'timeseries_shape': list(timeseries_df.shape),
            'tabular_shape': list(tabular_df.shape),
            'tabular_columns': list(tabular_df.columns),
            'statistics': {
                'diabetes_distribution': tabular_df['diabetes'].value_counts().to_dict(),
                'bp_distribution': tabular_df['bp_status'].value_counts().to_dict(),
                'diabetic_rbs_mean': round(diabetic_stats['mean'], 1),
                'diabetic_rbs_std': round(diabetic_stats['std'], 1),
                'non_diabetic_rbs_mean': round(non_diabetic_stats['mean'], 1),
                'non_diabetic_rbs_std': round(non_diabetic_stats['std'], 1),
                'age_range': f"{int(tabular_df['age'].min())}-{int(tabular_df['age'].max())}",
                'bmi_range': f"{tabular_df['bmi'].min():.1f}-{tabular_df['bmi'].max():.1f}",
                'hba1c_range': f"{tabular_df['hba1c'].min():.2f}-{tabular_df['hba1c'].max():.2f}"
            },
            'sample_patients': []
        }

        # Add sample patients
        for i in range(min(20, len(tabular_df))):
            patient_id = tabular_df.iloc[i]['patient_id']
            patient_ts = timeseries_df[timeseries_df['patient_id'] == patient_id]

            sample = {
                'patient_id': patient_id,
                'tabular_data': tabular_df.iloc[i].to_dict(),
                'timeseries_sample': patient_ts.head(5).to_dict('records')
            }
            preview['sample_patients'].append(sample)

        return preview
