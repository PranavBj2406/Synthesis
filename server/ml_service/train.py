# import logging
# import torch
# import torch.nn as nn
# from typing import Dict
# from tqdm import tqdm
# from data_utils import DiabetesDataPreprocessor
# from models import DiabetesPredictor
# from config import EPOCHS, DEFAULT_TIME_SERIES_PATH, DEFAULT_TABULAR_PATH
# from sklearn.metrics import accuracy_score, classification_report

# logger = logging.getLogger(__name__)

# class DiabetesTrainer:
#     def __init__(self):
#         self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
#         self.model = None
#         self.preprocessor = DiabetesDataPreprocessor()

#     def train_model(self, time_series_path: str = None, tabular_path: str = None, epochs: int = EPOCHS, learning_rate: float = 0.001) -> Dict:
#         """Train diabetes prediction model."""
#         logger.info("Starting diabetes prediction model training...")
        
#         # Use default paths if not provided
#         ts_path = time_series_path or DEFAULT_TIME_SERIES_PATH
#         tab_path = tabular_path or DEFAULT_TABULAR_PATH
        
#         # Load and preprocess data
#         merged_data = self.preprocessor.load_and_preprocess_data(ts_path, tab_path)
#         time_series, tabular, conditions, targets = self.preprocessor.preprocess_for_model(merged_data)
        
#         # Split data into train/validation
#         train_size = int(0.8 * len(time_series))
        
#         train_ts, val_ts = time_series[:train_size], time_series[train_size:]
#         train_tab, val_tab = tabular[:train_size], tabular[train_size:]
#         train_targets, val_targets = targets[:train_size], targets[train_size:]
        
#         # Create data loaders
#         train_loader = self.preprocessor.create_dataloader(train_ts, train_tab, conditions[:train_size], train_targets)
#         val_loader = self.preprocessor.create_dataloader(val_ts, val_tab, conditions[train_size:], val_targets)
        
#         # Initialize model
#         self.model = DiabetesPredictor().to(self.device)
        
#         # Loss functions and optimizer
#         criterion = nn.BCELoss()
#         optimizer = torch.optim.Adam(self.model.parameters(), lr=learning_rate)
#         scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=10)
        
#         # Training history
#         history = {
#             'train_loss': [], 'val_loss': [],
#             'diabetes_acc': [], 'bp_acc': [],
#             'overall_acc': []
#         }
        
#         best_val_loss = float('inf')
        
#         # Training loop
#         for epoch in range(epochs):
#             # Training phase
#             train_loss = self._train_epoch(train_loader, criterion, optimizer)
            
#             # Validation phase
#             val_loss, diabetes_acc, bp_acc, overall_acc = self._validate_epoch(val_loader, criterion)
            
#             # Update scheduler
#             scheduler.step(val_loss)
            
#             # Update history
#             history['train_loss'].append(train_loss)
#             history['val_loss'].append(val_loss)
#             history['diabetes_acc'].append(diabetes_acc)
#             history['bp_acc'].append(bp_acc)
#             history['overall_acc'].append(overall_acc)
            
#             # Save best model
#             if val_loss < best_val_loss:
#                 best_val_loss = val_loss
#                 torch.save(self.model.state_dict(), 'best_diabetes_model.pth')
            
#             # Log progress
#             if (epoch + 1) % 10 == 0:
#                 logger.info(f"Epoch {epoch+1}/{epochs} - Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}, "
#                            f"Diabetes Acc: {diabetes_acc:.4f}, BP Acc: {bp_acc:.4f}")
        
#         logger.info("Training completed successfully")
#         return history

#     def _train_epoch(self, data_loader, criterion, optimizer):
#         self.model.train()
#         total_loss = 0
        
#         for batch_idx, (rbs_seq, tabular, cond, targets) in enumerate(data_loader):
#             rbs_seq = rbs_seq.to(self.device)
#             tabular = tabular.to(self.device)
#             targets = targets.to(self.device)
            
#             optimizer.zero_grad()
            
#             # Forward pass
#             diabetes_pred, bp_pred = self.model(rbs_seq, tabular)
            
#             # Calculate losses
#             diabetes_loss = criterion(diabetes_pred.squeeze(), targets[:, 0])
#             bp_loss = criterion(bp_pred.squeeze(), targets[:, 1])
#             total_loss_batch = diabetes_loss + bp_loss
            
#             # Backward pass
#             total_loss_batch.backward()
#             optimizer.step()
            
#             total_loss += total_loss_batch.item()
        
#         return total_loss / len(data_loader)

#     def _validate_epoch(self, data_loader, criterion):
#         self.model.eval()
#         total_loss = 0
#         all_diabetes_preds = []
#         all_bp_preds = []
#         all_diabetes_targets = []
#         all_bp_targets = []
        
#         with torch.no_grad():
#             for rbs_seq, tabular, cond, targets in data_loader:
#                 rbs_seq = rbs_seq.to(self.device)
#                 tabular = tabular.to(self.device)
#                 targets = targets.to(self.device)
                
#                 # Forward pass
#                 diabetes_pred, bp_pred = self.model(rbs_seq, tabular)
                
#                 # Calculate losses
#                 diabetes_loss = criterion(diabetes_pred.squeeze(), targets[:, 0])
#                 bp_loss = criterion(bp_pred.squeeze(), targets[:, 1])
#                 total_loss += (diabetes_loss + bp_loss).item()
                
#                 # Collect predictions and targets
#                 all_diabetes_preds.extend((diabetes_pred.squeeze() > 0.5).cpu().numpy())
#                 all_bp_preds.extend((bp_pred.squeeze() > 0.5).cpu().numpy())
#                 all_diabetes_targets.extend(targets[:, 0].cpu().numpy())
#                 all_bp_targets.extend(targets[:, 1].cpu().numpy())
        
#         # Calculate accuracies
#         diabetes_acc = accuracy_score(all_diabetes_targets, all_diabetes_preds)
#         bp_acc = accuracy_score(all_bp_targets, all_bp_preds)
#         overall_acc = (diabetes_acc + bp_acc) / 2
        
#         return total_loss / len(data_loader), diabetes_acc, bp_acc, overall_acc

#     def predict(self, rbs_sequence, tabular_features):
#         """Make predictions for new data."""
#         if self.model is None:
#             raise RuntimeError("Model not trained. Please train model first.")
        
#         self.model.eval()
#         with torch.no_grad():
#             rbs_tensor = torch.FloatTensor(rbs_sequence).unsqueeze(0).unsqueeze(-1)
#             tab_tensor = torch.FloatTensor(tabular_features).unsqueeze(0)
            
#             diabetes_prob, bp_prob = self.model(rbs_tensor, tab_tensor)
            
#             return {
#                 'diabetes_probability': float(diabetes_prob.squeeze()),
#                 'bp_probability': float(bp_prob.squeeze()),
#                 'diabetes_prediction': int(diabetes_prob.squeeze() > 0.5),
#                 'bp_prediction': int(bp_prob.squeeze() > 0.5)
#             }

import logging
import torch
import torch.nn as nn
from typing import Dict
from tqdm import tqdm
from data_utils import DiabetesDataPreprocessor
from models import DiabetesPredictor
from config import EPOCHS, DEFAULT_TIME_SERIES_PATH, DEFAULT_TABULAR_PATH
from sklearn.metrics import accuracy_score, classification_report

logger = logging.getLogger(__name__)

class DiabetesTrainer:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.preprocessor = DiabetesDataPreprocessor()

    def train_model(self, time_series_path: str = None, tabular_path: str = None, epochs: int = EPOCHS, learning_rate: float = 0.001) -> Dict:
        """Train diabetes prediction model."""
        logger.info("Starting diabetes prediction model training...")
        
        # Use default paths if not provided
        ts_path = time_series_path or DEFAULT_TIME_SERIES_PATH
        tab_path = tabular_path or DEFAULT_TABULAR_PATH
        
        # Load and preprocess data
        merged_data = self.preprocessor.load_and_preprocess_data(ts_path, tab_path)
        time_series, tabular, conditions, targets = self.preprocessor.preprocess_for_model(merged_data)
        
        # Split data into train/validation
        train_size = int(0.8 * len(time_series))
        
        train_ts, val_ts = time_series[:train_size], time_series[train_size:]
        train_tab, val_tab = tabular[:train_size], tabular[train_size:]
        train_targets, val_targets = targets[:train_size], targets[train_size:]
        
        # Create data loaders
        train_loader = self.preprocessor.create_dataloader(train_ts, train_tab, conditions[:train_size], train_targets)
        val_loader = self.preprocessor.create_dataloader(val_ts, val_tab, conditions[train_size:], val_targets)
        
        # Initialize model
        self.model = DiabetesPredictor().to(self.device)
        
        # Loss functions and optimizer
        criterion = nn.BCELoss()
        optimizer = torch.optim.Adam(self.model.parameters(), lr=learning_rate)
        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=10)
        
        # Training history
        history = {
            'train_loss': [], 'val_loss': [],
            'diabetes_acc': [], 'bp_acc': [],
            'overall_acc': []
        }
        
        best_val_loss = float('inf')
        
        # Training loop
        for epoch in range(epochs):
            # Training phase
            train_loss = self._train_epoch(train_loader, criterion, optimizer)
            
            # Validation phase
            val_loss, diabetes_acc, bp_acc, overall_acc = self._validate_epoch(val_loader, criterion)
            
            # Update scheduler
            scheduler.step(val_loss)
            
            # Update history
            history['train_loss'].append(train_loss)
            history['val_loss'].append(val_loss)
            history['diabetes_acc'].append(diabetes_acc)
            history['bp_acc'].append(bp_acc)
            history['overall_acc'].append(overall_acc)
            
            # Save best model
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                torch.save(self.model.state_dict(), 'best_diabetes_model.pth')
            
            # Log progress
            if (epoch + 1) % 10 == 0:
                logger.info(f"Epoch {epoch+1}/{epochs} - Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}, "
                           f"Diabetes Acc: {diabetes_acc:.4f}, BP Acc: {bp_acc:.4f}")
        
        logger.info("Training completed successfully")
        return history

    def _train_epoch(self, data_loader, criterion, optimizer):
        self.model.train()
        total_loss = 0
        
        for batch_idx, (rbs_seq, tabular, cond, targets) in enumerate(data_loader):
            rbs_seq = rbs_seq.to(self.device)
            tabular = tabular.to(self.device)
            targets = targets.to(self.device)
            
            optimizer.zero_grad()
            
            # Forward pass
            diabetes_pred, bp_pred = self.model(rbs_seq, tabular)
            
            # Calculate losses
            diabetes_loss = criterion(diabetes_pred.squeeze(), targets[:, 0])
            bp_loss = criterion(bp_pred.squeeze(), targets[:, 1])
            total_loss_batch = diabetes_loss + bp_loss
            
            # Backward pass
            total_loss_batch.backward()
            optimizer.step()
            
            total_loss += total_loss_batch.item()
        
        return total_loss / len(data_loader)

    def _validate_epoch(self, data_loader, criterion):
        self.model.eval()
        total_loss = 0
        all_diabetes_preds = []
        all_bp_preds = []
        all_diabetes_targets = []
        all_bp_targets = []
        
        with torch.no_grad():
            for rbs_seq, tabular, cond, targets in data_loader:
                rbs_seq = rbs_seq.to(self.device)
                tabular = tabular.to(self.device)
                targets = targets.to(self.device)
                
                # Forward pass
                diabetes_pred, bp_pred = self.model(rbs_seq, tabular)
                
                # Calculate losses
                diabetes_loss = criterion(diabetes_pred.squeeze(), targets[:, 0])
                bp_loss = criterion(bp_pred.squeeze(), targets[:, 1])
                total_loss += (diabetes_loss + bp_loss).item()
                
                # Collect predictions and targets
                all_diabetes_preds.extend((diabetes_pred.squeeze() > 0.5).cpu().numpy())
                all_bp_preds.extend((bp_pred.squeeze() > 0.5).cpu().numpy())
                all_diabetes_targets.extend(targets[:, 0].cpu().numpy())
                all_bp_targets.extend(targets[:, 1].cpu().numpy())
        
        # Calculate accuracies
        diabetes_acc = accuracy_score(all_diabetes_targets, all_diabetes_preds)
        bp_acc = accuracy_score(all_bp_targets, all_bp_preds)
        overall_acc = (diabetes_acc + bp_acc) / 2
        
        return total_loss / len(data_loader), diabetes_acc, bp_acc, overall_acc

    def predict(self, rbs_sequence, tabular_features):
        """Make predictions for new data."""
        if self.model is None:
            raise RuntimeError("Model not trained. Please train model first.")
        
        self.model.eval()
        with torch.no_grad():
            rbs_tensor = torch.FloatTensor(rbs_sequence).unsqueeze(0).unsqueeze(-1)
            tab_tensor = torch.FloatTensor(tabular_features).unsqueeze(0)
            
            diabetes_prob, bp_prob = self.model(rbs_tensor, tab_tensor)
            
            return {
                'diabetes_probability': float(diabetes_prob.squeeze()),
                'bp_probability': float(bp_prob.squeeze()),
                'diabetes_prediction': int(diabetes_prob.squeeze() > 0.5),
                'bp_prediction': int(bp_prob.squeeze() > 0.5)
            }
