import logging
import torch
import torch.nn as nn
from typing import Dict
from tqdm import tqdm
from data_utils import DataPreprocessor
from model_registry import model_registry
from config import EPOCHS, LATENT_DIM

logger = logging.getLogger(__name__)

class Trainer:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
    def train_models(self, time_series_path: str, tabular_path: str, epochs: int = EPOCHS) -> Dict:
        """Train all models."""
        logger.info("Starting training process...")
        
        # Initialize data preprocessor
        preprocessor = DataPreprocessor()
        
        # Load and preprocess data
        merged_data = preprocessor.load_and_preprocess_data(time_series_path, tabular_path)
        time_series, tabular, conditions = preprocessor.preprocess_for_model(merged_data)
        
        # Create dataloader
        data_loader = preprocessor.create_dataloader(time_series, tabular, conditions)
        logger.info(f"Created dataloader with {len(data_loader)} batches")
        
        # Initialize models
        model_registry.initialize_models()
        
        # Get models
        ts_generator, tab_generator, cross_modal_generator = model_registry.ts_generator, model_registry.tab_generator, model_registry.cross_modal_generator
        ts_discriminator, tab_discriminator = model_registry.ts_discriminator, model_registry.tab_discriminator
        
        # Initialize optimizers
        optimizers = self._setup_optimizers(ts_generator, tab_generator, cross_modal_generator, ts_discriminator, tab_discriminator)
        
        # Loss functions
        criterion = nn.BCELoss()
        cross_criterion = nn.MSELoss()
        
        # Training history
        metrics_history = {
            'ts_gen_loss': [], 'ts_dis_loss': [],
            'tab_gen_loss': [], 'tab_dis_loss': [],
            'cross_loss': []
        }
        
        # Training loop
        for epoch in range(epochs):
            epoch_metrics = self._train_epoch(
                data_loader, ts_generator, tab_generator, cross_modal_generator,
                ts_discriminator, tab_discriminator, optimizers, criterion, cross_criterion, epoch
            )
            
            # Update history
            for key in metrics_history:
                metrics_history[key].append(epoch_metrics[key])
                
            # Log epoch summary
            logger.info(f"Epoch {epoch+1}/{epochs} - "
                       f"TS G/D: {epoch_metrics['ts_gen_loss']:.4f}/{epoch_metrics['ts_dis_loss']:.4f} - "
                       f"Tab G/D: {epoch_metrics['tab_gen_loss']:.4f}/{epoch_metrics['tab_dis_loss']:.4f} - "
                       f"Cross: {epoch_metrics['cross_loss']:.4f}")
        
        # Set models to eval mode
        for model in [ts_generator, tab_generator, cross_modal_generator]:
            model.eval()
            
        # Save training history
        model_registry.set_training_history(metrics_history)
        
        # Save models
        timestamp = model_registry.save_models(epochs)
        
        logger.info("Training completed successfully")
        return metrics_history
        
    def _setup_optimizers(self, ts_gen, tab_gen, cross_gen, ts_dis, tab_dis):
        """Setup optimizers for all models."""
        return {
            'ts_g': torch.optim.Adam(ts_gen.parameters(), lr=0.0002, betas=(0.5, 0.999)),
            'tab_g': torch.optim.Adam(tab_gen.parameters(), lr=0.0002, betas=(0.5, 0.999)),
            'cross': torch.optim.Adam(cross_gen.parameters(), lr=0.0002, betas=(0.5, 0.999)),
            'ts_d': torch.optim.Adam(ts_dis.parameters(), lr=0.0002, betas=(0.5, 0.999)),
            'tab_d': torch.optim.Adam(tab_dis.parameters(), lr=0.0002, betas=(0.5, 0.999))
        }
        
    def _train_epoch(self, data_loader, ts_gen, tab_gen, cross_gen, ts_dis, tab_dis, optimizers, criterion, cross_criterion, epoch):
        """Train one epoch."""
        epoch_metrics = {
            'ts_gen_loss': 0, 'ts_dis_loss': 0,
            'tab_gen_loss': 0, 'tab_dis_loss': 0,
            'cross_loss': 0
        }
        
        batch_count = 0
        
        for batch_idx, (real_ts, real_tab, cond) in enumerate(tqdm(data_loader, desc=f"Epoch {epoch+1}")):
            real_ts, real_tab, cond = real_ts.to(self.device), real_tab.to(self.device), cond.to(self.device)
            batch_size = real_ts.size(0)
            batch_count += 1
            
            # Create noise vector
            z = torch.randn(batch_size, LATENT_DIM, device=self.device)
            
            # Train discriminators
            ts_d_loss = self._train_discriminator(ts_dis, ts_gen, real_ts, cond, z, optimizers['ts_d'], criterion)
            tab_d_loss = self._train_discriminator(tab_dis, tab_gen, real_tab, cond, z, optimizers['tab_d'], criterion)
            
            # Train generators
            ts_g_loss = self._train_generator(ts_gen, ts_dis, cond, z, optimizers['ts_g'], criterion)
            tab_g_loss = self._train_generator(tab_gen, tab_dis, cond, z, optimizers['tab_g'], criterion)
            
            # Train cross-modal generator
            cross_loss = self._train_cross_modal(cross_gen, real_ts, real_tab, cond, optimizers['cross'], cross_criterion)
            
            # Update metrics
            epoch_metrics['ts_gen_loss'] += ts_g_loss
            epoch_metrics['ts_dis_loss'] += ts_d_loss
            epoch_metrics['tab_gen_loss'] += tab_g_loss
            epoch_metrics['tab_dis_loss'] += tab_d_loss
            epoch_metrics['cross_loss'] += cross_loss
            
        # Average metrics
        for key in epoch_metrics:
            epoch_metrics[key] /= batch_count
            
        return epoch_metrics
        
    def _train_discriminator(self, discriminator, generator, real_data, cond, z, optimizer, criterion):
        """Train discriminator."""
        optimizer.zero_grad()
        
        # Real samples
        real_pred = discriminator(real_data, cond)
        real_loss = criterion(real_pred, torch.ones_like(real_pred))
        
        # Fake samples
        with torch.no_grad():
            fake_data = generator(z, cond)
        fake_pred = discriminator(fake_data.detach(), cond)
        fake_loss = criterion(fake_pred, torch.zeros_like(fake_pred))
        
        # Combined loss
        d_loss = (real_loss + fake_loss) / 2
        d_loss.backward()
        optimizer.step()
        
        return d_loss.item()
        
    def _train_generator(self, generator, discriminator, cond, z, optimizer, criterion):
        """Train generator."""
        optimizer.zero_grad()
        
        fake_data = generator(z, cond)
        fake_pred = discriminator(fake_data, cond)
        g_loss = criterion(fake_pred, torch.ones_like(fake_pred))
        
        g_loss.backward()
        optimizer.step()
        
        return g_loss.item()
        
    def _train_cross_modal(self, cross_gen, real_ts, real_tab, cond, optimizer, criterion):
        """Train cross-modal generator."""
        optimizer.zero_grad()
        
        # Time series to tabular
        generated_tab = cross_gen.generate_tab_from_ts(real_ts, cond)
        tab_recon_loss = criterion(generated_tab, real_tab)
        
        # Tabular to time series
        generated_ts = cross_gen.generate_ts_from_tab(real_tab, cond)
        ts_recon_loss = criterion(generated_ts, real_ts)
        
        # Combined loss
        cross_loss = ts_recon_loss + tab_recon_loss
        cross_loss.backward()
        optimizer.step()
        
        return cross_loss.item()
