import torch
import torch.nn as nn
from config import *

class Attention(nn.Module):
    def __init__(self, hidden_dim):
        super().__init__()
        self.attn = nn.Linear(hidden_dim, 1)

    def forward(self, x):
        weights = torch.softmax(self.attn(x), dim=1)
        return x * weights

class DiabetesPredictor(nn.Module):
    """Main prediction model for diabetes and BP status."""
    def __init__(self):
        super().__init__()
        
        # Calculate the actual input size for tabular features
        # We have 7 original features, but hypertension becomes 2 features (systolic + diastolic)
        actual_tabular_size = len([f for f in TABULAR_FEATURES if f != 'hypertension']) + 2  # +2 for systolic/diastolic
        
        # Time series encoder for RBS values
        self.rbs_encoder = nn.LSTM(input_size=1, hidden_size=HIDDEN_DIM, batch_first=True, dropout=0.2)
        self.attention = Attention(HIDDEN_DIM)
        
        # Tabular feature encoder
        self.tabular_encoder = nn.Sequential(
            nn.Linear(actual_tabular_size, 128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, 64),
            nn.ReLU()
        )
        
        # Combined feature fusion
        self.fusion = nn.Sequential(
            nn.Linear(HIDDEN_DIM + 64, 128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, 64),
            nn.ReLU()
        )
        
        # Separate heads for diabetes and BP prediction
        self.diabetes_head = nn.Sequential(
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
        
        self.bp_head = nn.Sequential(
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )

    def forward(self, rbs_sequence, tabular_features):
        # Process RBS time series
        rbs_output, (hidden, _) = self.rbs_encoder(rbs_sequence)
        rbs_features = hidden[-1]  # Use last hidden state
        
        # Process tabular features
        tabular_encoded = self.tabular_encoder(tabular_features)
        
        # Fuse features
        combined = torch.cat([rbs_features, tabular_encoded], dim=1)
        fused = self.fusion(combined)
        
        # Make predictions
        diabetes_pred = self.diabetes_head(fused)
        bp_pred = self.bp_head(fused)
        
        return diabetes_pred, bp_pred

# [Rest of the models remain the same...]
class TabularGenerator(nn.Module):
    """Generator for synthetic tabular data."""
    def __init__(self):
        super().__init__()
        # Adjust for the actual number of features (including split hypertension)
        actual_tabular_size = len([f for f in TABULAR_FEATURES if f != 'hypertension']) + 2
        self.model = nn.Sequential(
            nn.Linear(LATENT_DIM + len(COND_FEATURES), 256),
            nn.ReLU(),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, actual_tabular_size),
            nn.Sigmoid()
        )

    def forward(self, z, cond):
        x = torch.cat([z, cond], dim=1)
        return self.model(x)

class TimeSeriesGenerator(nn.Module):
    """Generator for synthetic RBS time series."""
    def __init__(self):
        super().__init__()
        self.fc = nn.Sequential(
            nn.Linear(LATENT_DIM + len(COND_FEATURES), 256),
            nn.ReLU(),
            nn.Linear(256, SEQ_LENGTH * HIDDEN_DIM),
            nn.ReLU()
        )
        
        self.attn = Attention(HIDDEN_DIM)
        self.out = nn.Linear(HIDDEN_DIM, 1)  # Only RBS values

    def forward(self, z, cond):
        x = torch.cat([z, cond], dim=1)
        x = self.fc(x).view(-1, SEQ_LENGTH, HIDDEN_DIM)
        x = self.attn(x)
        return torch.sigmoid(self.out(x))

class TabularDiscriminator(nn.Module):
    def __init__(self):
        super().__init__()
        actual_tabular_size = len([f for f in TABULAR_FEATURES if f != 'hypertension']) + 2
        self.model = nn.Sequential(
            nn.Linear(actual_tabular_size + len(COND_FEATURES), 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 1),
            nn.Sigmoid()
        )

    def forward(self, x, cond):
        x = torch.cat([x, cond], dim=1)
        return self.model(x)

class TimeSeriesDiscriminator(nn.Module):
    def __init__(self):
        super().__init__()
        self.lstm = nn.LSTM(input_size=1, hidden_size=HIDDEN_DIM, batch_first=True)
        self.fc = nn.Sequential(
            nn.Linear(HIDDEN_DIM + len(COND_FEATURES), 128),
            nn.ReLU(),
            nn.Linear(128, 1),
            nn.Sigmoid()
        )

    def forward(self, x, cond):
        output, (h_n, _) = self.lstm(x)
        x = torch.cat([h_n.squeeze(0), cond], dim=1)
        return self.fc(x)

class CrossModalGenerator(nn.Module):
    def __init__(self):
        super().__init__()
        actual_tabular_size = len([f for f in TABULAR_FEATURES if f != 'hypertension']) + 2
        
        # Tabular to time series
        self.tab_to_ts = nn.Sequential(
            nn.Linear(actual_tabular_size + len(COND_FEATURES), 256),
            nn.ReLU(),
            nn.Linear(256, SEQ_LENGTH * 1),
            nn.Sigmoid()
        )
        
        # Time series encoder
        self.ts_encoder = nn.LSTM(1, HIDDEN_DIM, batch_first=True)
        
        # Time series to tabular
        self.ts_to_tab = nn.Sequential(
            nn.Linear(HIDDEN_DIM + len(COND_FEATURES), 128),
            nn.ReLU(),
            nn.Linear(128, actual_tabular_size),
            nn.Sigmoid()
        )

    def generate_ts_from_tab(self, tab, cond):
        x = torch.cat([tab, cond], dim=1)
        return self.tab_to_ts(x).view(-1, SEQ_LENGTH, 1)

    def generate_tab_from_ts(self, ts, cond):
        _, (h_n, _) = self.ts_encoder(ts)
        x = torch.cat([h_n.squeeze(0), cond], dim=1)
        return self.ts_to_tab(x)
