# import pandas as pd
# import numpy as np
# from datetime import datetime, timedelta
# import random

# # Set random seed for reproducibility
# np.random.seed(42)
# random.seed(42)

# print("Generating Time Series Dataset for Diabetes Monitoring...")

# # Parameters for time series dataset
# num_patients = 200  # To get 20000+ records with 10 hours per day over multiple days
# hours_per_day = 10
# days_per_patient = 10  # This will give us 200 * 10 * 10 = 20,000 records

# # Generate time series dataset
# timeseries_data = []

# for patient_id in range(1, num_patients + 1):
#     # Generate base RBS pattern for each patient (some diabetic, some normal)
#     is_diabetic = random.choice([True, False])
    
#     if is_diabetic:
#         # Diabetic patients: higher baseline RBS with more variation
#         base_rbs = np.random.normal(250, 40)  # Higher mean RBS
#         daily_variation = 60
#     else:
#         # Non-diabetic patients: normal RBS range
#         base_rbs = np.random.normal(140, 25)  # Normal mean RBS
#         daily_variation = 30
    
#     # Generate data for multiple days
#     start_date = datetime(2024, 1, 1)
    
#     for day in range(days_per_patient):
#         current_date = start_date + timedelta(days=day)
        
#         # Daily RBS pattern (typically higher in morning, varies throughout day)
#         daily_multiplier = np.random.normal(1.0, 0.1)
        
#         for hour in range(hours_per_day):
#             # Create realistic hourly timestamps (8 AM to 5 PM)
#             timestamp = current_date.replace(hour=8+hour, minute=0, second=0)
            
#             # Generate RBS values with realistic patterns
#             # Morning hours (8-10 AM): slightly higher due to dawn phenomenon
#             # Post-meal hours: potential spikes
#             # Evening: usually lower
            
#             if hour <= 2:  # Morning (8-10 AM)
#                 hour_multiplier = np.random.normal(1.1, 0.1)
#             elif hour in [3, 4, 7, 8]:  # Post-meal times
#                 hour_multiplier = np.random.normal(1.2, 0.15)
#             else:  # Other times
#                 hour_multiplier = np.random.normal(0.95, 0.1)
            
#             # Calculate RBS value
#             rbs_value = base_rbs * daily_multiplier * hour_multiplier
            
#             # Add some random variation and ensure within bounds
#             rbs_value += np.random.normal(0, 15)
#             rbs_value = max(100, min(400, rbs_value))  # Constrain to specified range
            
#             timeseries_data.append({
#                 'patient_id': f'P{patient_id:04d}',
#                 'timestamp': timestamp,
#                 'rbs_value': round(rbs_value, 1)
#             })

# # Create DataFrame
# timeseries_df = pd.DataFrame(timeseries_data)

# print("Generating Tabular Dataset for Diabetes Diagnosis...")

# # Generate tabular dataset
# tabular_data = []

# # Calculate average RBS for each patient from time series data
# patient_avg_rbs = timeseries_df.groupby('patient_id')['rbs_value'].mean().to_dict()

# for patient_id_key, avg_rbs in patient_avg_rbs.items():
#     # Extract numeric patient ID
#     patient_num = int(patient_id_key[1:])
    
#     # Generate age between 30-55
#     age = np.random.randint(30, 56)
    
#     # Generate HbA1c based on RBS pattern with realistic correlation
#     # HbA1c reflects 2-3 month average glucose levels
#     # Normal: < 5.7%, Prediabetic: 5.7-6.4%, Diabetic: ≥ 6.5%
    
#     if avg_rbs > 250:  # High RBS
#         # Likely diabetic range HbA1c
#         hba1c = np.random.normal(6.8, 0.3)
#         hba1c = max(6.2, min(7.0, hba1c))  # Constrain to reasonable diabetic range
#     elif avg_rbs > 180:  # Moderate RBS
#         # Prediabetic to mild diabetic range
#         hba1c = np.random.normal(6.1, 0.4)
#         hba1c = max(5.7, min(7.0, hba1c))
#     else:  # Lower RBS
#         # Normal to prediabetic range
#         hba1c = np.random.normal(5.8, 0.2)
#         hba1c = max(5.72, min(6.5, hba1c))
    
#     # Ensure HbA1c is within specified bounds
#     hba1c = max(5.72, min(7.0, hba1c))
    
#     # Determine outcome based on specified rules
#     # Outcome = 1 if average RBS > 200 AND HbA1c > 6.7
#     # Outcome = 0 if average RBS < 200 AND HbA1c < 5.7
#     # For intermediate cases, use clinical logic
    
#     if avg_rbs > 200 and hba1c > 6.7:
#         outcome = 1  # Diabetic
#     elif avg_rbs < 200 and hba1c < 5.7:
#         outcome = 0  # Non-diabetic
#     else:
#         # Intermediate cases - use additional clinical logic
#         if avg_rbs > 200 or hba1c > 6.4:
#             outcome = 1  # Likely diabetic
#         else:
#             outcome = 0  # Likely non-diabetic
    
#     # Add some additional realistic medical parameters
#     # BMI correlation with diabetes
#     if outcome == 1:
#         bmi = np.random.normal(28.5, 4.0)  # Higher BMI for diabetics
#     else:
#         bmi = np.random.normal(24.5, 3.0)  # Normal BMI range
    
#     bmi = max(18.5, min(40.0, bmi))  # Reasonable BMI bounds
    
#     # Family history (higher probability for diabetics)
#     family_history = 1 if (outcome == 1 and random.random() < 0.7) or (outcome == 0 and random.random() < 0.3) else 0
    
#     # Hypertension correlation
#     hypertension = 1 if (outcome == 1 and random.random() < 0.6) or (outcome == 0 and random.random() < 0.2) else 0
    
#     tabular_data.append({
#         'patient_id': patient_id_key,
#         'age': age,
#         'bmi': round(bmi, 1),
#         'average_rbs': round(avg_rbs, 1),
#         'hba1c': round(hba1c, 2),
#         'family_history': family_history,
#         'hypertension': hypertension,
#         'outcome': outcome
#     })

# # Create DataFrame
# tabular_df = pd.DataFrame(tabular_data)

# # Save datasets to CSV files
# timeseries_df.to_csv('diabetes_timeseries_dataset.csv', index=False)
# tabular_df.to_csv('diabetes_tabular_dataset.csv', index=False)

# print("✅ Datasets generated successfully!")
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

print("Generating Enhanced Time Series Dataset for Diabetes Monitoring...")

# Parameters for time series dataset
# Need 20000+ records with 13 hours per day (6 AM to 6 PM) per patient
hours_per_day = 13  # 6 AM to 6 PM inclusive (13 time points)
num_patients = int(20000 / hours_per_day) + 1  # ~1539 patients to get 20000+ records

# Generate time series dataset
timeseries_data = []
base_date = datetime(2024, 9, 26)  # Single date for all patients

for patient_id in range(1, num_patients + 1):
    # Determine patient diabetes status and characteristics
    is_diabetic = random.choice([True, False])
    
    if is_diabetic:
        base_rbs = np.random.normal(280, 50)  # Higher mean RBS for diabetics
        rbs_variability = 40
    else:
        base_rbs = np.random.normal(130, 25)  # Normal mean RBS
        rbs_variability = 20
    
    daily_pattern = np.random.normal(1.0, 0.05)
    
    for hour_offset in range(hours_per_day):
        current_hour = 6 + hour_offset
        timestamp = base_date.replace(hour=current_hour, minute=0, second=0)
        
        # Generate realistic RBS patterns throughout the day
        if hour_offset <= 2:  # 6-8 AM: Dawn phenomenon
            time_multiplier = np.random.normal(1.05, 0.1)
        elif hour_offset in [3, 4]:  # 9-10 AM: Post-breakfast
            time_multiplier = np.random.normal(1.25, 0.15)
        elif hour_offset in [6, 7]:  # 12-1 PM: Post-lunch
            time_multiplier = np.random.normal(1.20, 0.12)
        elif hour_offset in [8, 9]:  # 2-3 PM: Post-meal continuation
            time_multiplier = np.random.normal(1.10, 0.10)
        else:  # Other times: baseline
            time_multiplier = np.random.normal(0.95, 0.08)
        
        rbs_value = base_rbs * daily_pattern * time_multiplier
        rbs_value += np.random.normal(0, rbs_variability * 0.3)
        rbs_value = max(100, min(400, round(rbs_value, 1)))
        
        timeseries_data.append({
            'patient_id': f'P{patient_id:05d}',
            'timestamp': timestamp,
            'rbs_value': rbs_value
        })

# Create time series DataFrame
timeseries_df = pd.DataFrame(timeseries_data)

print("Generating Enhanced Tabular Dataset for Diabetes Diagnosis...")

# Generate comprehensive tabular dataset
tabular_data = []
patient_avg_rbs = timeseries_df.groupby('patient_id')['rbs_value'].mean().to_dict()

for patient_id_key, avg_rbs in patient_avg_rbs.items():
    patient_num = int(patient_id_key[1:])
    age = np.random.randint(30, 56)
    
    # Generate HbA1c with realistic correlation to average RBS
    if avg_rbs > 280:
        hba1c = np.random.normal(6.9, 0.15)
        hba1c = max(6.5, min(7.0, hba1c))
    elif avg_rbs > 220:
        hba1c = np.random.normal(6.3, 0.3)
        hba1c = max(6.0, min(7.0, hba1c))
    elif avg_rbs > 160:
        hba1c = np.random.normal(5.9, 0.2)
        hba1c = max(5.7, min(6.8, hba1c))
    else:
        hba1c = np.random.normal(5.8, 0.15)
        hba1c = max(5.72, min(6.2, hba1c))
    
    hba1c = max(5.72, min(7.0, hba1c))
    
    # Determine diabetes outcome based on specified rules
    if avg_rbs > 200 and hba1c > 6.7:
        diabetes = 1
    elif avg_rbs < 200 and hba1c < 5.7:
        diabetes = 0
    else:
        diabetes = 1 if (avg_rbs > 200 or hba1c > 6.4) else 0
    
    # Generate Blood Pressure with realistic correlations
    if diabetes == 1:
        systolic_base = np.random.normal(135, 20)
        diastolic_base = np.random.normal(85, 12)
    else:
        systolic_base = np.random.normal(115, 15)
        diastolic_base = np.random.normal(75, 8)
    
    age_bp_factor = 1 + (age - 40) * 0.01
    systolic = max(100, min(180, round(systolic_base * age_bp_factor)))
    diastolic = max(70, min(120, round(diastolic_base * age_bp_factor)))
    
    if diastolic > systolic - 20:
        diastolic = max(70, systolic - 20)
    
    hypertension = f"{int(systolic)}/{int(diastolic)}"
    bp_status = 0 if (systolic <= 120 and diastolic <= 80) else 1
    
    # Generate vital signs
    rr = max(12, min(18, round(np.random.normal(16 if diabetes == 1 else 14, 1.5))))
    hr = max(70, min(100, round(np.random.normal(82 if diabetes == 1 else 75, 8) + (age - 42) * 0.3)))
    
    if diabetes == 1 and random.random() < 0.1:
        spo2 = max(95, min(100, round(np.random.normal(96.5, 1.0), 1)))
    else:
        spo2 = max(95, min(100, round(np.random.normal(98.5, 1.0), 1)))
    
    bmi = max(18.5, min(45.0, round(np.random.normal(29.0 if diabetes == 1 else 24.0, 4.5 if diabetes == 1 else 3.0), 1)))
    
    tabular_data.append({
        'patient_id': patient_id_key,
        'age': age,
        'bmi': bmi,
        'average_rbs': round(avg_rbs, 1),
        'hba1c': round(hba1c, 2),
        'hypertension': hypertension,
        'bp_status': bp_status,
        'respiratory_rate': int(rr),
        'heart_rate': int(hr),
        'spo2': spo2,
        'diabetes': diabetes
    })

# Create tabular DataFrame
tabular_df = pd.DataFrame(tabular_data)

# Save datasets
timeseries_df.to_csv('enhanced_diabetes_timeseries_dataset.csv', index=False)
tabular_df.to_csv('enhanced_diabetes_tabular_dataset.csv', index=False)

print("✅ Enhanced datasets generated successfully!")
