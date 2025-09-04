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

class TabularGenerator(nn.Module):
    def __init__(self):
        super().__init__()
        self.model = nn.Sequential(
            nn.Linear(LATENT_DIM + len(COND_FEATURES), 256),
            nn.ReLU(),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, len(TABULAR_FEATURES)),
            nn.Sigmoid()
        )

    def forward(self, z, cond):
        x = torch.cat([z, cond], dim=1)
        return self.model(x)

class TimeSeriesGenerator(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc = nn.Sequential(
            nn.Linear(LATENT_DIM + len(COND_FEATURES), 256),
            nn.ReLU(),
            nn.Linear(256, SEQ_LENGTH * HIDDEN_DIM),
            nn.ReLU()
        )
        self.attn = Attention(HIDDEN_DIM)
        self.out = nn.Linear(HIDDEN_DIM, len(FEATURES))

    def forward(self, z, cond):
        x = torch.cat([z, cond], dim=1)
        x = self.fc(x).view(-1, SEQ_LENGTH, HIDDEN_DIM)
        x = self.attn(x)
        return torch.sigmoid(self.out(x))

class TabularDiscriminator(nn.Module):
    def __init__(self):
        super().__init__()
        self.model = nn.Sequential(
            nn.Linear(len(TABULAR_FEATURES) + len(COND_FEATURES), 128),
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
        self.lstm = nn.LSTM(input_size=len(FEATURES), hidden_size=HIDDEN_DIM, batch_first=True)
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
        self.tab_to_ts = nn.Sequential(
            nn.Linear(len(TABULAR_FEATURES) + len(COND_FEATURES), 256),
            nn.ReLU(),
            nn.Linear(256, SEQ_LENGTH * len(FEATURES)),
            nn.Sigmoid()
        )
        
        self.ts_encoder = nn.LSTM(len(FEATURES), HIDDEN_DIM, batch_first=True)
        self.ts_to_tab = nn.Sequential(
            nn.Linear(HIDDEN_DIM + len(COND_FEATURES), 128),
            nn.ReLU(),
            nn.Linear(128, len(TABULAR_FEATURES)),
            nn.Sigmoid()
        )

    def generate_ts_from_tab(self, tab, cond):
        x = torch.cat([tab, cond], dim=1)
        return self.tab_to_ts(x).view(-1, SEQ_LENGTH, len(FEATURES))

    def generate_tab_from_ts(self, ts, cond):
        _, (h_n, _) = self.ts_encoder(ts)
        x = torch.cat([h_n.squeeze(0), cond], dim=1)
        return self.ts_to_tab(x)
