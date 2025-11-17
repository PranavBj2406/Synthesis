# import torch
# import torch.nn as nn
# from config import *

# # ==================== ATTENTION MECHANISM ====================
# class Attention(nn.Module):
#     """Attention mechanism for focusing on important features."""
#     def __init__(self, hidden_dim):
#         super().__init__()
#         self.attn = nn.Linear(hidden_dim, 1)

#     def forward(self, x):
#         weights = torch.softmax(self.attn(x), dim=1)
#         return x * weights

# # ==================== PREDICTION MODEL (Supervised) ====================
# class DiabetesPredictor(nn.Module):
#     """Main prediction model for diabetes and BP status - Supervised Learning."""
#     def __init__(self):
#         super().__init__()
        
#         actual_tabular_size = len([f for f in TABULAR_FEATURES if f != 'hypertension']) + 2
        
#         # Time series encoder for RBS values
#         self.rbs_encoder = nn.LSTM(input_size=1, hidden_size=HIDDEN_DIM, batch_first=True)
#         self.attention = Attention(HIDDEN_DIM)
        
#         # Tabular feature encoder
#         self.tabular_encoder = nn.Sequential(
#             nn.Linear(actual_tabular_size, 128),
#             nn.BatchNorm1d(128),
#             nn.ReLU(),
#             nn.Dropout(0.3),
#             nn.Linear(128, 64),
#             nn.BatchNorm1d(64),
#             nn.ReLU()
#         )
        
#         # Combined feature fusion
#         self.fusion = nn.Sequential(
#             nn.Linear(HIDDEN_DIM + 64, 128),
#             nn.BatchNorm1d(128),
#             nn.ReLU(),
#             nn.Dropout(0.3),
#             nn.Linear(128, 64),
#             nn.BatchNorm1d(64),
#             nn.ReLU()
#         )
        
#         # Separate heads for diabetes and BP prediction
#         self.diabetes_head = nn.Sequential(
#             nn.Linear(64, 32),
#             nn.ReLU(),
#             nn.Dropout(0.2),
#             nn.Linear(32, 1),
#             nn.Sigmoid()
#         )
        
#         self.bp_head = nn.Sequential(
#             nn.Linear(64, 32),
#             nn.ReLU(),
#             nn.Dropout(0.2),
#             nn.Linear(32, 1),
#             nn.Sigmoid()
#         )

#     def forward(self, rbs_sequence, tabular_features):
#         rbs_output, (hidden, _) = self.rbs_encoder(rbs_sequence)
#         rbs_features = hidden[-1]
#         tabular_encoded = self.tabular_encoder(tabular_features)
#         combined = torch.cat([rbs_features, tabular_encoded], dim=1)
#         fused = self.fusion(combined)
#         diabetes_pred = self.diabetes_head(fused)
#         bp_pred = self.bp_head(fused)
#         return diabetes_pred, bp_pred

# # ==================== TABULAR GAN (CWGAN-GP) ====================
# class TabularGenerator(nn.Module):
#     """Conditional Wasserstein GAN Generator for Tabular Data with Spectral Normalization."""
#     def __init__(self):
#         super().__init__()
        
#         # Input: latent vector + condition features
#         input_dim = LATENT_DIM + len(COND_FEATURES)
#         # Output: 7 features (excluding hypertension) + 2 for BP (systolic/diastolic)
#         output_dim = len([f for f in TABULAR_FEATURES if f != 'hypertension']) + 2
        
#         self.model = nn.Sequential(
#             # Layer 1: Expansion
#             nn.Linear(input_dim, 256),
#             nn.LayerNorm(256),
#             nn.LeakyReLU(0.2),
#             nn.Dropout(0.2),
            
#             # Layer 2: Residual block
#             nn.Linear(256, 512),
#             nn.LayerNorm(512),
#             nn.LeakyReLU(0.2),
#             nn.Dropout(0.2),
            
#             # Layer 3: Feature extraction
#             nn.Linear(512, 256),
#             nn.LayerNorm(256),
#             nn.LeakyReLU(0.2),
            
#             # Layer 4: Refinement
#             nn.Linear(256, 128),
#             nn.LayerNorm(128),
#             nn.LeakyReLU(0.2),
            
#             # Output layer
#             nn.Linear(128, output_dim),
#             nn.Sigmoid()  # Normalize to [0, 1]
#         )
        
#         # Apply weight initialization
#         self.apply(self._init_weights)
    
#     def _init_weights(self, m):
#         if isinstance(m, nn.Linear):
#             nn.init.xavier_uniform_(m.weight)
#             if m.bias is not None:
#                 nn.init.constant_(m.bias, 0)

#     def forward(self, z, cond):
#         """
#         z: latent noise [batch_size, LATENT_DIM]
#         cond: condition features [batch_size, len(COND_FEATURES)]
#         """
#         x = torch.cat([z, cond], dim=1)
#         return self.model(x)

# class TabularDiscriminator(nn.Module):
#     """Conditional Wasserstein GAN Discriminator (Critic) for Tabular Data."""
#     def __init__(self):
#         super().__init__()
        
#         input_dim = len([f for f in TABULAR_FEATURES if f != 'hypertension']) + 2 + len(COND_FEATURES)
        
#         self.model = nn.Sequential(
#             # Layer 1
#             nn.Linear(input_dim, 128),
#             nn.LayerNorm(128),
#             nn.LeakyReLU(0.2),
#             nn.Dropout(0.3),
            
#             # Layer 2
#             nn.Linear(128, 256),
#             nn.LayerNorm(256),
#             nn.LeakyReLU(0.2),
#             nn.Dropout(0.3),
            
#             # Layer 3
#             nn.Linear(256, 128),
#             nn.LayerNorm(128),
#             nn.LeakyReLU(0.2),
#             nn.Dropout(0.3),
            
#             # Layer 4
#             nn.Linear(128, 64),
#             nn.LayerNorm(64),
#             nn.LeakyReLU(0.2),
            
#             # Output layer (Wasserstein: no sigmoid, output real values)
#             nn.Linear(64, 1)
#         )
        
#         self.apply(self._init_weights)
    
#     def _init_weights(self, m):
#         if isinstance(m, nn.Linear):
#             nn.init.xavier_uniform_(m.weight)
#             if m.bias is not None:
#                 nn.init.constant_(m.bias, 0)

#     def forward(self, x, cond):
#         """
#         x: tabular features [batch_size, features]
#         cond: condition features [batch_size, len(COND_FEATURES)]
#         """
#         x = torch.cat([x, cond], dim=1)
#         return self.model(x)

# # ==================== TIME SERIES GAN (CWGAN-GP with LSTM) ====================
# class TimeSeriesGenerator(nn.Module):
#     """Conditional GAN Generator for Time Series (RBS) with LSTM."""
#     def __init__(self):
#         super().__init__()
        
#         input_dim = LATENT_DIM + len(COND_FEATURES)
        
#         # Fully connected to initial hidden state
#         self.fc = nn.Sequential(
#             nn.Linear(input_dim, 256),
#             nn.LayerNorm(256),
#             nn.LeakyReLU(0.2),
#             nn.Linear(256, SEQ_LENGTH * HIDDEN_DIM),
#             nn.LayerNorm(SEQ_LENGTH * HIDDEN_DIM),
#             nn.LeakyReLU(0.2)
#         )
        
#         # LSTM for temporal dependencies
#         self.lstm = nn.LSTM(
#             input_size=HIDDEN_DIM,
#             hidden_size=HIDDEN_DIM,
#             num_layers=2,
#             batch_first=True,
#             dropout=0.2
#         )
        
#         # Attention mechanism
#         self.attn = Attention(HIDDEN_DIM)
        
#         # Output projection
#         self.out = nn.Sequential(
#             nn.Linear(HIDDEN_DIM, 64),
#             nn.LayerNorm(64),
#             nn.LeakyReLU(0.2),
#             nn.Linear(64, 1),
#             nn.Sigmoid()  # RBS values normalized to [0, 1]
#         )
        
#         self.apply(self._init_weights)
    
#     def _init_weights(self, m):
#         if isinstance(m, (nn.Linear, nn.LSTM)):
#             if isinstance(m, nn.Linear):
#                 nn.init.xavier_uniform_(m.weight)
#                 if m.bias is not None:
#                     nn.init.constant_(m.bias, 0)

#     def forward(self, z, cond):
#         """
#         z: latent noise [batch_size, LATENT_DIM]
#         cond: condition features [batch_size, len(COND_FEATURES)]
#         """
#         x = torch.cat([z, cond], dim=1)
#         x = self.fc(x)
#         x = x.view(-1, SEQ_LENGTH, HIDDEN_DIM)
#         x, _ = self.lstm(x)
#         x = self.attn(x)
#         x = self.out(x)
#         return x

# class TimeSeriesDiscriminator(nn.Module):
#     """Conditional Wasserstein GAN Discriminator (Critic) for Time Series."""
#     def __init__(self):
#         super().__init__()
        
#         # LSTM encoder
#         self.lstm = nn.LSTM(
#             input_size=1,
#             hidden_size=HIDDEN_DIM,
#             num_layers=2,
#             batch_first=True,
#             dropout=0.2
#         )
        
#         # Critic network
#         self.fc = nn.Sequential(
#             nn.Linear(HIDDEN_DIM + len(COND_FEATURES), 256),
#             nn.LayerNorm(256),
#             nn.LeakyReLU(0.2),
#             nn.Dropout(0.3),
            
#             nn.Linear(256, 128),
#             nn.LayerNorm(128),
#             nn.LeakyReLU(0.2),
#             nn.Dropout(0.3),
            
#             nn.Linear(128, 64),
#             nn.LayerNorm(64),
#             nn.LeakyReLU(0.2),
            
#             nn.Linear(64, 1)  # Wasserstein: output real values
#         )
        
#         self.apply(self._init_weights)
    
#     def _init_weights(self, m):
#         if isinstance(m, (nn.Linear, nn.LSTM)):
#             if isinstance(m, nn.Linear):
#                 nn.init.xavier_uniform_(m.weight)
#                 if m.bias is not None:
#                     nn.init.constant_(m.bias, 0)

#     def forward(self, x, cond):
#         """
#         x: time series [batch_size, SEQ_LENGTH, 1]
#         cond: condition features [batch_size, len(COND_FEATURES)]
#         """
#         _, (h_n, _) = self.lstm(x)
#         x = h_n[-1]  # Use last layer's hidden state
#         x = torch.cat([x, cond], dim=1)
#         return self.fc(x)

# # ==================== CROSS-MODAL GENERATOR ====================
# class CrossModalGenerator(nn.Module):
#     """Cross-modal generator for translating between tabular and time series."""
#     def __init__(self):
#         super().__init__()
        
#         tabular_size = len([f for f in TABULAR_FEATURES if f != 'hypertension']) + 2
        
#         # Tabular to Time Series
#         self.tab_to_ts = nn.Sequential(
#             nn.Linear(tabular_size + len(COND_FEATURES), 256),
#             nn.LayerNorm(256),
#             nn.LeakyReLU(0.2),
#             nn.Dropout(0.2),
            
#             nn.Linear(256, 512),
#             nn.LayerNorm(512),
#             nn.LeakyReLU(0.2),
            
#             nn.Linear(512, SEQ_LENGTH * HIDDEN_DIM),
#             nn.LayerNorm(SEQ_LENGTH * HIDDEN_DIM),
#             nn.LeakyReLU(0.2)
#         )
        
#         # LSTM for temporal structure
#         self.lstm = nn.LSTM(HIDDEN_DIM, HIDDEN_DIM, batch_first=True)
        
#         # Output projection
#         self.ts_out = nn.Sequential(
#             nn.Linear(HIDDEN_DIM, 32),
#             nn.LeakyReLU(0.2),
#             nn.Linear(32, 1),
#             nn.Sigmoid()
#         )
        
#         # Time Series to Tabular
#         self.ts_encoder = nn.LSTM(1, HIDDEN_DIM, num_layers=2, batch_first=True)
        
#         self.ts_to_tab = nn.Sequential(
#             nn.Linear(HIDDEN_DIM + len(COND_FEATURES), 256),
#             nn.LayerNorm(256),
#             nn.LeakyReLU(0.2),
#             nn.Dropout(0.2),
            
#             nn.Linear(256, 128),
#             nn.LayerNorm(128),
#             nn.LeakyReLU(0.2),
            
#             nn.Linear(128, tabular_size),
#             nn.Sigmoid()
#         )

#     def generate_ts_from_tab(self, tab, cond):
#         """Generate time series from tabular data."""
#         x = torch.cat([tab, cond], dim=1)
#         x = self.tab_to_ts(x)
#         x = x.view(-1, SEQ_LENGTH, HIDDEN_DIM)
#         x, _ = self.lstm(x)
#         x = self.ts_out(x)
#         return x

#     def generate_tab_from_ts(self, ts, cond):
#         """Generate tabular data from time series."""
#         _, (h_n, _) = self.ts_encoder(ts)
#         x = h_n[-1]  # Use last layer's hidden state
#         x = torch.cat([x, cond], dim=1)
#         return self.ts_to_tab(x)
import torch
import torch.nn as nn
from config import *

# ==================== ATTENTION MECHANISM ====================
class Attention(nn.Module):
    """Attention mechanism for focusing on important features."""
    def __init__(self, hidden_dim):
        super().__init__()
        self.attn = nn.Linear(hidden_dim, 1)
    
    def forward(self, x):
        weights = torch.softmax(self.attn(x), dim=1)
        return x * weights

# ==================== TABULAR GAN (CWGAN-GP) ====================
class TabularGenerator(nn.Module):
    """Conditional Wasserstein GAN Generator for Tabular Data."""
    def __init__(self):
        super().__init__()
        input_dim = LATENT_DIM + len(COND_FEATURES)
        output_dim = len([f for f in TABULAR_FEATURES if f != 'hypertension']) + 2
        
        self.model = nn.Sequential(
            nn.Linear(input_dim, 256),
            nn.LayerNorm(256),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.2),
            nn.Linear(256, 512),
            nn.LayerNorm(512),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.2),
            nn.Linear(512, 256),
            nn.LayerNorm(256),
            nn.LeakyReLU(0.2),
            nn.Linear(256, 128),
            nn.LayerNorm(128),
            nn.LeakyReLU(0.2),
            nn.Linear(128, output_dim),
            nn.Sigmoid()
        )
        self.apply(self._init_weights)
    
    def _init_weights(self, m):
        if isinstance(m, nn.Linear):
            nn.init.xavier_uniform_(m.weight)
            if m.bias is not None:
                nn.init.constant_(m.bias, 0)
    
    def forward(self, z, cond):
        x = torch.cat([z, cond], dim=1)
        return self.model(x)

class TabularDiscriminator(nn.Module):
    """Conditional Wasserstein GAN Discriminator for Tabular Data."""
    def __init__(self):
        super().__init__()
        input_dim = len([f for f in TABULAR_FEATURES if f != 'hypertension']) + 2 + len(COND_FEATURES)
        
        self.model = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.LayerNorm(128),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.3),
            nn.Linear(128, 256),
            nn.LayerNorm(256),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.3),
            nn.Linear(256, 128),
            nn.LayerNorm(128),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.3),
            nn.Linear(128, 64),
            nn.LayerNorm(64),
            nn.LeakyReLU(0.2),
            nn.Linear(64, 1)
        )
        self.apply(self._init_weights)
    
    def _init_weights(self, m):
        if isinstance(m, nn.Linear):
            nn.init.xavier_uniform_(m.weight)
            if m.bias is not None:
                nn.init.constant_(m.bias, 0)
    
    def forward(self, x, cond):
        x = torch.cat([x, cond], dim=1)
        return self.model(x)

# ==================== TIME SERIES GAN ====================
class TimeSeriesGenerator(nn.Module):
    """Conditional GAN Generator for Time Series (RBS) with LSTM."""
    def __init__(self):
        super().__init__()
        input_dim = LATENT_DIM + len(COND_FEATURES)
        
        self.fc = nn.Sequential(
            nn.Linear(input_dim, 256),
            nn.LayerNorm(256),
            nn.LeakyReLU(0.2),
            nn.Linear(256, SEQ_LENGTH * HIDDEN_DIM),
            nn.LayerNorm(SEQ_LENGTH * HIDDEN_DIM),
            nn.LeakyReLU(0.2)
        )
        
        self.lstm = nn.LSTM(
            input_size=HIDDEN_DIM,
            hidden_size=HIDDEN_DIM,
            num_layers=2,
            batch_first=True,
            dropout=0.2
        )
        
        self.attn = Attention(HIDDEN_DIM)
        
        self.out = nn.Sequential(
            nn.Linear(HIDDEN_DIM, 64),
            nn.LayerNorm(64),
            nn.LeakyReLU(0.2),
            nn.Linear(64, 1),
            nn.Sigmoid()
        )
        self.apply(self._init_weights)
    
    def _init_weights(self, m):
        if isinstance(m, (nn.Linear, nn.LSTM)):
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)
    
    def forward(self, z, cond):
        x = torch.cat([z, cond], dim=1)
        x = self.fc(x)
        x = x.view(-1, SEQ_LENGTH, HIDDEN_DIM)
        x, _ = self.lstm(x)
        x = self.attn(x)
        x = self.out(x)
        return x

class TimeSeriesDiscriminator(nn.Module):
    """Conditional Wasserstein GAN Discriminator for Time Series."""
    def __init__(self):
        super().__init__()
        
        self.lstm = nn.LSTM(
            input_size=1,
            hidden_size=HIDDEN_DIM,
            num_layers=2,
            batch_first=True,
            dropout=0.2
        )
        
        self.fc = nn.Sequential(
            nn.Linear(HIDDEN_DIM + len(COND_FEATURES), 256),
            nn.LayerNorm(256),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.3),
            nn.Linear(256, 128),
            nn.LayerNorm(128),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.3),
            nn.Linear(128, 64),
            nn.LayerNorm(64),
            nn.LeakyReLU(0.2),
            nn.Linear(64, 1)
        )
        self.apply(self._init_weights)
    
    def _init_weights(self, m):
        if isinstance(m, (nn.Linear, nn.LSTM)):
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)
    
    def forward(self, x, cond):
        _, (h_n, _) = self.lstm(x)
        x = h_n[-1]
        x = torch.cat([x, cond], dim=1)
        return self.fc(x)

# ==================== CROSS-MODAL GENERATOR ====================
class CrossModalGenerator(nn.Module):
    """Cross-modal generator for translating between tabular and time series."""
    def __init__(self):
        super().__init__()
        tabular_size = len([f for f in TABULAR_FEATURES if f != 'hypertension']) + 2
        
        self.tab_to_ts = nn.Sequential(
            nn.Linear(tabular_size + len(COND_FEATURES), 256),
            nn.LayerNorm(256),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.2),
            nn.Linear(256, 512),
            nn.LayerNorm(512),
            nn.LeakyReLU(0.2),
            nn.Linear(512, SEQ_LENGTH * HIDDEN_DIM),
            nn.LayerNorm(SEQ_LENGTH * HIDDEN_DIM),
            nn.LeakyReLU(0.2)
        )
        
        self.lstm = nn.LSTM(HIDDEN_DIM, HIDDEN_DIM, batch_first=True)
        
        self.ts_out = nn.Sequential(
            nn.Linear(HIDDEN_DIM, 32),
            nn.LeakyReLU(0.2),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
        
        self.ts_encoder = nn.LSTM(1, HIDDEN_DIM, num_layers=2, batch_first=True)
        
        self.ts_to_tab = nn.Sequential(
            nn.Linear(HIDDEN_DIM + len(COND_FEATURES), 256),
            nn.LayerNorm(256),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.2),
            nn.Linear(256, 128),
            nn.LayerNorm(128),
            nn.LeakyReLU(0.2),
            nn.Linear(128, tabular_size),
            nn.Sigmoid()
        )
    
    def generate_ts_from_tab(self, tab, cond):
        """Generate time series from tabular data."""
        x = torch.cat([tab, cond], dim=1)
        x = self.tab_to_ts(x)
        x = x.view(-1, SEQ_LENGTH, HIDDEN_DIM)
        x, _ = self.lstm(x)
        x = self.ts_out(x)
        return x
    
    def generate_tab_from_ts(self, ts, cond):
        """Generate tabular data from time series."""
        _, (h_n, _) = self.ts_encoder(ts)
        x = h_n[-1]
        x = torch.cat([x, cond], dim=1)
        return self.ts_to_tab(x)
