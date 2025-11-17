
# import logging
# import torch
# import torch.nn as nn
# from typing import Dict
# import numpy as np
# from tqdm import tqdm
# import os

# from models import (
#     TabularGenerator, TabularDiscriminator,
#     TimeSeriesGenerator, TimeSeriesDiscriminator,
#     CrossModalGenerator
# )
# from data_utils import DiabetesDataPreprocessor
# from config import EPOCHS, LATENT_DIM, BATCH_SIZE, MODEL_DIR

# logger = logging.getLogger(__name__)

# class GANTrainer:
#     """Trainer for Conditional Wasserstein GAN with Gradient Penalty."""
    
#     def __init__(self, lambda_gp: float = 10.0, n_critic: int = 5):
#         """
#         Args:
#             lambda_gp: Gradient penalty coefficient
#             n_critic: Number of critic updates per generator update
#         """
#         self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
#         self.lambda_gp = lambda_gp
#         self.n_critic = n_critic

#         # Initialize models
#         self.tab_gen = TabularGenerator().to(self.device)
#         self.tab_disc = TabularDiscriminator().to(self.device)
#         self.ts_gen = TimeSeriesGenerator().to(self.device)
#         self.ts_disc = TimeSeriesDiscriminator().to(self.device)
#         self.cross_modal = CrossModalGenerator().to(self.device)

#         logger.info(f"[OK] GAN Trainer initialized on device: {self.device}")

#     def compute_gradient_penalty(self, discriminator, real_data, fake_data, conditions):
#         """Compute gradient penalty for Wasserstein GAN."""
#         batch_size = real_data.size(0)

#         # Random weight for interpolation
#         alpha = torch.rand(batch_size, 1, device=self.device)

#         # Expand alpha to match data dimensions
#         if len(real_data.shape) == 3:  # Time series
#             alpha = alpha.unsqueeze(2).expand_as(real_data)
#         else:  # Tabular
#             alpha = alpha.expand_as(real_data)

#         # Interpolate between real and fake data
#         interpolates = alpha * real_data + (1 - alpha) * fake_data
#         interpolates.requires_grad_(True)

#         # Get discriminator output
#         disc_interpolates = discriminator(interpolates, conditions)

#         # Compute gradients
#         gradients = torch.autograd.grad(
#             outputs=disc_interpolates,
#             inputs=interpolates,
#             grad_outputs=torch.ones_like(disc_interpolates),
#             create_graph=True,
#             retain_graph=True,
#             only_inputs=True
#         )[0]

#         # Flatten gradients
#         gradients = gradients.view(batch_size, -1)

#         # Compute gradient penalty
#         gradient_penalty = ((gradients.norm(2, dim=1) - 1) ** 2).mean()

#         return gradient_penalty

#     def train_gan(self, time_series_path: str, tabular_path: str, epochs: int = 100) -> Dict:
#         """Train all GAN models."""
#         logger.info("=" * 60)
#         logger.info("Starting GAN training...")
#         logger.info(f"Epochs: {epochs} | Device: {self.device}")
#         logger.info("=" * 60)

#         # Load and preprocess data
#         preprocessor = DiabetesDataPreprocessor()
#         merged_data = preprocessor.load_and_preprocess_data(time_series_path, tabular_path)
#         time_series, tabular, conditions, _ = preprocessor.preprocess_for_model(merged_data)

#         logger.info(f"[OK] Data loaded - Samples: {len(time_series)}")
#         logger.info(f"[OK] Tabular features: {tabular.shape}")
#         logger.info(f"[OK] Time series shape: {time_series.shape}")

#         # Create dataloader
#         dataloader = preprocessor.create_dataloader(time_series, tabular, conditions, conditions)

#         # Optimizers with recommended hyperparameters for WGAN-GP
#         tab_gen_opt = torch.optim.Adam(self.tab_gen.parameters(), lr=0.0001, betas=(0.5, 0.9))
#         tab_disc_opt = torch.optim.Adam(self.tab_disc.parameters(), lr=0.0001, betas=(0.5, 0.9))
#         ts_gen_opt = torch.optim.Adam(self.ts_gen.parameters(), lr=0.0001, betas=(0.5, 0.9))
#         ts_disc_opt = torch.optim.Adam(self.ts_disc.parameters(), lr=0.0001, betas=(0.5, 0.9))
#         cross_opt = torch.optim.Adam(self.cross_modal.parameters(), lr=0.0001, betas=(0.5, 0.9))

#         # Training history
#         history = {
#             'tab_gen_loss': [], 'tab_disc_loss': [],
#             'ts_gen_loss': [], 'ts_disc_loss': [],
#             'cross_modal_loss': []
#         }

#         best_gen_loss = float('inf')

#         # Training loop
#         for epoch in range(epochs):
#             tab_gen_losses, tab_disc_losses = [], []
#             ts_gen_losses, ts_disc_losses = [], []
#             cross_losses = []

#             pbar = tqdm(dataloader, desc=f"Epoch {epoch+1}/{epochs}")

#             for batch_idx, (ts_batch, tab_batch, cond_batch, _) in enumerate(pbar):
#                 ts_batch = ts_batch.to(self.device)
#                 tab_batch = tab_batch.to(self.device)
#                 cond_batch = cond_batch.to(self.device)
#                 batch_size = ts_batch.size(0)

#                 # ============ Train Tabular Discriminator ============
#                 for _ in range(self.n_critic):
#                     tab_disc_opt.zero_grad()

#                     # Generate fake tabular data
#                     z = torch.randn(batch_size, LATENT_DIM, device=self.device)
#                     fake_tab = self.tab_gen(z, cond_batch)

#                     # Discriminator outputs
#                     real_validity = self.tab_disc(tab_batch, cond_batch)
#                     fake_validity = self.tab_disc(fake_tab.detach(), cond_batch)

#                     # Gradient penalty
#                     gp = self.compute_gradient_penalty(self.tab_disc, tab_batch, fake_tab, cond_batch)

#                     # Wasserstein loss
#                     tab_disc_loss = -torch.mean(real_validity) + torch.mean(fake_validity) + self.lambda_gp * gp

#                     tab_disc_loss.backward()
#                     torch.nn.utils.clip_grad_norm_(self.tab_disc.parameters(), max_norm=1.0)
#                     tab_disc_opt.step()

#                     tab_disc_losses.append(tab_disc_loss.item())

#                 # ============ Train Tabular Generator ============
#                 tab_gen_opt.zero_grad()
#                 z = torch.randn(batch_size, LATENT_DIM, device=self.device)
#                 fake_tab = self.tab_gen(z, cond_batch)
#                 fake_validity = self.tab_disc(fake_tab, cond_batch)

#                 tab_gen_loss = -torch.mean(fake_validity)

#                 tab_gen_loss.backward()
#                 torch.nn.utils.clip_grad_norm_(self.tab_gen.parameters(), max_norm=1.0)
#                 tab_gen_opt.step()

#                 tab_gen_losses.append(tab_gen_loss.item())

#                 # ============ Train Time Series Discriminator ============
#                 for _ in range(self.n_critic):
#                     ts_disc_opt.zero_grad()

#                     z = torch.randn(batch_size, LATENT_DIM, device=self.device)
#                     fake_ts = self.ts_gen(z, cond_batch)

#                     real_validity = self.ts_disc(ts_batch, cond_batch)
#                     fake_validity = self.ts_disc(fake_ts.detach(), cond_batch)

#                     gp = self.compute_gradient_penalty(self.ts_disc, ts_batch, fake_ts, cond_batch)

#                     ts_disc_loss = -torch.mean(real_validity) + torch.mean(fake_validity) + self.lambda_gp * gp

#                     ts_disc_loss.backward()
#                     torch.nn.utils.clip_grad_norm_(self.ts_disc.parameters(), max_norm=1.0)
#                     ts_disc_opt.step()

#                     ts_disc_losses.append(ts_disc_loss.item())

#                 # ============ Train Time Series Generator ============
#                 ts_gen_opt.zero_grad()
#                 z = torch.randn(batch_size, LATENT_DIM, device=self.device)
#                 fake_ts = self.ts_gen(z, cond_batch)
#                 fake_validity = self.ts_disc(fake_ts, cond_batch)

#                 ts_gen_loss = -torch.mean(fake_validity)

#                 ts_gen_loss.backward()
#                 torch.nn.utils.clip_grad_norm_(self.ts_gen.parameters(), max_norm=1.0)
#                 ts_gen_opt.step()

#                 ts_gen_losses.append(ts_gen_loss.item())

#                 # ============ Train Cross-Modal Generator ============
#                 cross_opt.zero_grad()

#                 # Tabular to Time Series
#                 fake_ts_from_tab = self.cross_modal.generate_ts_from_tab(tab_batch, cond_batch)
#                 ts_reconstruction_loss = nn.MSELoss()(fake_ts_from_tab, ts_batch)

#                 # Time Series to Tabular
#                 fake_tab_from_ts = self.cross_modal.generate_tab_from_ts(ts_batch, cond_batch)
#                 tab_reconstruction_loss = nn.MSELoss()(fake_tab_from_ts, tab_batch)

#                 cross_modal_loss = ts_reconstruction_loss + tab_reconstruction_loss

#                 cross_modal_loss.backward()
#                 torch.nn.utils.clip_grad_norm_(self.cross_modal.parameters(), max_norm=1.0)
#                 cross_opt.step()

#                 cross_losses.append(cross_modal_loss.item())

#                 # Update progress bar
#                 pbar.set_postfix({
#                     'TabD': f'{np.mean(tab_disc_losses[-10:]):.4f}',
#                     'TabG': f'{np.mean(tab_gen_losses[-10:]):.4f}',
#                     'TsD': f'{np.mean(ts_disc_losses[-10:]):.4f}',
#                     'TsG': f'{np.mean(ts_gen_losses[-10:]):.4f}',
#                     'Cross': f'{np.mean(cross_losses[-10:]):.4f}'
#                 })

#             # Record epoch losses
#             history['tab_gen_loss'].append(np.mean(tab_gen_losses))
#             history['tab_disc_loss'].append(np.mean(tab_disc_losses))
#             history['ts_gen_loss'].append(np.mean(ts_gen_losses))
#             history['ts_disc_loss'].append(np.mean(ts_disc_losses))
#             history['cross_modal_loss'].append(np.mean(cross_losses))

#             # Save best model based on generator loss
#             current_gen_loss = (np.mean(tab_gen_losses) + np.mean(ts_gen_losses)) / 2
#             if current_gen_loss < best_gen_loss:
#                 best_gen_loss = current_gen_loss
#                 self.save_models()
#                 logger.info(f"[OK] Best models saved at epoch {epoch+1} with loss: {best_gen_loss:.4f}")

#             # Log progress
#             if (epoch + 1) % 10 == 0:
#                 logger.info(f"Epoch {epoch+1}/{epochs} - "
#                            f"TabGenLoss: {history['tab_gen_loss'][-1]:.4f}, "
#                            f"TsGenLoss: {history['ts_gen_loss'][-1]:.4f}, "
#                            f"CrossLoss: {history['cross_modal_loss'][-1]:.4f}")

#         # Save final models
#         self.save_models()
#         logger.info("=" * 60)
#         logger.info("[OK] GAN training completed successfully")
#         logger.info(f"[OK] Models saved to: {MODEL_DIR}")
#         logger.info("=" * 60)

#         return history

#     def save_models(self):
#         """Save all GAN models with detailed logging."""
#         os.makedirs(MODEL_DIR, exist_ok=True)
        
#         model_files = {
#             "tabular_generator.pth": self.tab_gen.state_dict(),
#             "tabular_discriminator.pth": self.tab_disc.state_dict(),
#             "timeseries_generator.pth": self.ts_gen.state_dict(),
#             "timeseries_discriminator.pth": self.ts_disc.state_dict(),
#             "cross_modal_generator.pth": self.cross_modal.state_dict()
#         }
        
#         for filename, state_dict in model_files.items():
#             filepath = os.path.join(MODEL_DIR, filename)
#             torch.save(state_dict, filepath)
#             logger.info(f"[OK] Saved: {filepath}")

#     def load_models(self):
#         """Load all GAN models with proper device mapping and detailed logging."""
#         try:
#             # Check if model files exist
#             model_files = [
#                 f"{MODEL_DIR}/tabular_generator.pth",
#                 f"{MODEL_DIR}/timeseries_generator.pth",
#                 f"{MODEL_DIR}/cross_modal_generator.pth"
#             ]

#             missing_files = [f for f in model_files if not os.path.exists(f)]
#             if missing_files:
#                 logger.warning(f"[WARNING] GAN model files not found: {missing_files}")
#                 return False

#             # Load with proper device mapping
#             logger.info(f"Loading GAN models from: {MODEL_DIR}")
            
#             self.tab_gen.load_state_dict(
#                 torch.load(f"{MODEL_DIR}/tabular_generator.pth", map_location=self.device)
#             )
#             self.tab_disc.load_state_dict(
#                 torch.load(f"{MODEL_DIR}/tabular_discriminator.pth", map_location=self.device)
#             )
#             self.ts_gen.load_state_dict(
#                 torch.load(f"{MODEL_DIR}/timeseries_generator.pth", map_location=self.device)
#             )
#             self.ts_disc.load_state_dict(
#                 torch.load(f"{MODEL_DIR}/timeseries_discriminator.pth", map_location=self.device)
#             )
#             self.cross_modal.load_state_dict(
#                 torch.load(f"{MODEL_DIR}/cross_modal_generator.pth", map_location=self.device)
#             )

#             # Set to evaluation mode
#             self.tab_gen.eval()
#             self.ts_gen.eval()
#             self.cross_modal.eval()

#             logger.info(f"[OK] GAN models loaded successfully from {MODEL_DIR}")
#             return True

#         except Exception as e:
#             logger.error(f"[ERROR] Failed to load GAN models: {str(e)}")
#             return False
import logging
import torch
import torch.nn as nn
from typing import Dict
import numpy as np
from tqdm import tqdm
import os

from models import (
    TabularGenerator, TabularDiscriminator,
    TimeSeriesGenerator, TimeSeriesDiscriminator,
    CrossModalGenerator
)
from data_utils import DiabetesDataPreprocessor
from config import EPOCHS, LATENT_DIM, BATCH_SIZE, MODEL_DIR

logger = logging.getLogger(__name__)

class GANTrainer:
    """Trainer for Conditional Wasserstein GAN with Gradient Penalty."""
    
    def __init__(self, lambda_gp: float = 10.0, n_critic: int = 5):
        """
        Args:
            lambda_gp: Gradient penalty coefficient
            n_critic: Number of critic updates per generator update
        """
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.lambda_gp = lambda_gp
        self.n_critic = n_critic

        # Initialize models
        self.tab_gen = TabularGenerator().to(self.device)
        self.tab_disc = TabularDiscriminator().to(self.device)
        self.ts_gen = TimeSeriesGenerator().to(self.device)
        self.ts_disc = TimeSeriesDiscriminator().to(self.device)
        self.cross_modal = CrossModalGenerator().to(self.device)

        logger.info(f"[OK] GAN Trainer initialized on device: {self.device}")

    def compute_gradient_penalty(self, discriminator, real_data, fake_data, conditions):
        """Compute gradient penalty for Wasserstein GAN."""
        batch_size = real_data.size(0)

        # Random weight for interpolation
        alpha = torch.rand(batch_size, 1, device=self.device)

        # Expand alpha to match data dimensions
        if len(real_data.shape) == 3:  # Time series
            alpha = alpha.unsqueeze(2).expand_as(real_data)
        else:  # Tabular
            alpha = alpha.expand_as(real_data)

        # Interpolate between real and fake data
        interpolates = alpha * real_data + (1 - alpha) * fake_data
        interpolates.requires_grad_(True)

        # Get discriminator output
        disc_interpolates = discriminator(interpolates, conditions)

        # Compute gradients
        gradients = torch.autograd.grad(
            outputs=disc_interpolates,
            inputs=interpolates,
            grad_outputs=torch.ones_like(disc_interpolates),
            create_graph=True,
            retain_graph=True,
            only_inputs=True
        )[0]

        # Flatten gradients
        gradients = gradients.view(batch_size, -1)

        # Compute gradient penalty
        gradient_penalty = ((gradients.norm(2, dim=1) - 1) ** 2).mean()

        return gradient_penalty

    def train_gan(self, time_series_path: str, tabular_path: str, epochs: int = 100) -> Dict:
        """Train all GAN models."""
        logger.info("=" * 60)
        logger.info("Starting GAN training...")
        logger.info(f"Epochs: {epochs} | Device: {self.device}")
        logger.info("=" * 60)

        # Load and preprocess data
        preprocessor = DiabetesDataPreprocessor()
        merged_data = preprocessor.load_and_preprocess_data(time_series_path, tabular_path)
        time_series, tabular, conditions, _ = preprocessor.preprocess_for_model(merged_data)

        logger.info(f"[OK] Data loaded - Samples: {len(time_series)}")
        logger.info(f"[OK] Tabular features: {tabular.shape}")
        logger.info(f"[OK] Time series shape: {time_series.shape}")

        # Create dataloader
        dataloader = preprocessor.create_dataloader(time_series, tabular, conditions, conditions)

        # Optimizers with recommended hyperparameters for WGAN-GP
        tab_gen_opt = torch.optim.Adam(self.tab_gen.parameters(), lr=0.0001, betas=(0.5, 0.9))
        tab_disc_opt = torch.optim.Adam(self.tab_disc.parameters(), lr=0.0001, betas=(0.5, 0.9))
        ts_gen_opt = torch.optim.Adam(self.ts_gen.parameters(), lr=0.0001, betas=(0.5, 0.9))
        ts_disc_opt = torch.optim.Adam(self.ts_disc.parameters(), lr=0.0001, betas=(0.5, 0.9))
        cross_opt = torch.optim.Adam(self.cross_modal.parameters(), lr=0.0001, betas=(0.5, 0.9))

        # Training history
        history = {
            'tab_gen_loss': [], 'tab_disc_loss': [],
            'ts_gen_loss': [], 'ts_disc_loss': [],
            'cross_modal_loss': []
        }

        best_gen_loss = float('inf')

        # Training loop
        for epoch in range(epochs):
            tab_gen_losses, tab_disc_losses = [], []
            ts_gen_losses, ts_disc_losses = [], []
            cross_losses = []

            pbar = tqdm(dataloader, desc=f"Epoch {epoch+1}/{epochs}")

            for batch_idx, (ts_batch, tab_batch, cond_batch, _) in enumerate(pbar):
                ts_batch = ts_batch.to(self.device)
                tab_batch = tab_batch.to(self.device)
                cond_batch = cond_batch.to(self.device)
                batch_size = ts_batch.size(0)

                # ============ Train Tabular Discriminator ============
                for _ in range(self.n_critic):
                    tab_disc_opt.zero_grad()

                    # Generate fake tabular data
                    z = torch.randn(batch_size, LATENT_DIM, device=self.device)
                    fake_tab = self.tab_gen(z, cond_batch)

                    # Discriminator outputs
                    real_validity = self.tab_disc(tab_batch, cond_batch)
                    fake_validity = self.tab_disc(fake_tab.detach(), cond_batch)

                    # Gradient penalty
                    gp = self.compute_gradient_penalty(self.tab_disc, tab_batch, fake_tab, cond_batch)

                    # Wasserstein loss
                    tab_disc_loss = -torch.mean(real_validity) + torch.mean(fake_validity) + self.lambda_gp * gp

                    tab_disc_loss.backward()
                    torch.nn.utils.clip_grad_norm_(self.tab_disc.parameters(), max_norm=1.0)
                    tab_disc_opt.step()

                    tab_disc_losses.append(tab_disc_loss.item())

                # ============ Train Tabular Generator ============
                tab_gen_opt.zero_grad()
                z = torch.randn(batch_size, LATENT_DIM, device=self.device)
                fake_tab = self.tab_gen(z, cond_batch)
                fake_validity = self.tab_disc(fake_tab, cond_batch)

                tab_gen_loss = -torch.mean(fake_validity)

                tab_gen_loss.backward()
                torch.nn.utils.clip_grad_norm_(self.tab_gen.parameters(), max_norm=1.0)
                tab_gen_opt.step()

                tab_gen_losses.append(tab_gen_loss.item())

                # ============ Train Time Series Discriminator ============
                for _ in range(self.n_critic):
                    ts_disc_opt.zero_grad()

                    z = torch.randn(batch_size, LATENT_DIM, device=self.device)
                    fake_ts = self.ts_gen(z, cond_batch)

                    real_validity = self.ts_disc(ts_batch, cond_batch)
                    fake_validity = self.ts_disc(fake_ts.detach(), cond_batch)

                    gp = self.compute_gradient_penalty(self.ts_disc, ts_batch, fake_ts, cond_batch)

                    ts_disc_loss = -torch.mean(real_validity) + torch.mean(fake_validity) + self.lambda_gp * gp

                    ts_disc_loss.backward()
                    torch.nn.utils.clip_grad_norm_(self.ts_disc.parameters(), max_norm=1.0)
                    ts_disc_opt.step()

                    ts_disc_losses.append(ts_disc_loss.item())

                # ============ Train Time Series Generator ============
                ts_gen_opt.zero_grad()
                z = torch.randn(batch_size, LATENT_DIM, device=self.device)
                fake_ts = self.ts_gen(z, cond_batch)
                fake_validity = self.ts_disc(fake_ts, cond_batch)

                ts_gen_loss = -torch.mean(fake_validity)

                ts_gen_loss.backward()
                torch.nn.utils.clip_grad_norm_(self.ts_gen.parameters(), max_norm=1.0)
                ts_gen_opt.step()

                ts_gen_losses.append(ts_gen_loss.item())

                # ============ Train Cross-Modal Generator ============
                cross_opt.zero_grad()

                # Tabular to Time Series
                fake_ts_from_tab = self.cross_modal.generate_ts_from_tab(tab_batch, cond_batch)
                ts_reconstruction_loss = nn.MSELoss()(fake_ts_from_tab, ts_batch)

                # Time Series to Tabular
                fake_tab_from_ts = self.cross_modal.generate_tab_from_ts(ts_batch, cond_batch)
                tab_reconstruction_loss = nn.MSELoss()(fake_tab_from_ts, tab_batch)

                cross_modal_loss = ts_reconstruction_loss + tab_reconstruction_loss

                cross_modal_loss.backward()
                torch.nn.utils.clip_grad_norm_(self.cross_modal.parameters(), max_norm=1.0)
                cross_opt.step()

                cross_losses.append(cross_modal_loss.item())

                # Update progress bar
                pbar.set_postfix({
                    'TabD': f'{np.mean(tab_disc_losses[-10:]):.4f}',
                    'TabG': f'{np.mean(tab_gen_losses[-10:]):.4f}',
                    'TsD': f'{np.mean(ts_disc_losses[-10:]):.4f}',
                    'TsG': f'{np.mean(ts_gen_losses[-10:]):.4f}',
                    'Cross': f'{np.mean(cross_losses[-10:]):.4f}'
                })

            # Record epoch losses
            history['tab_gen_loss'].append(np.mean(tab_gen_losses))
            history['tab_disc_loss'].append(np.mean(tab_disc_losses))
            history['ts_gen_loss'].append(np.mean(ts_gen_losses))
            history['ts_disc_loss'].append(np.mean(ts_disc_losses))
            history['cross_modal_loss'].append(np.mean(cross_losses))

            # Save best model based on generator loss
            current_gen_loss = (np.mean(tab_gen_losses) + np.mean(ts_gen_losses)) / 2
            if current_gen_loss < best_gen_loss:
                best_gen_loss = current_gen_loss
                self.save_models()
                logger.info(f"[OK] Best models saved at epoch {epoch+1} with loss: {best_gen_loss:.4f}")

            # Log progress
            if (epoch + 1) % 10 == 0:
                logger.info(f"Epoch {epoch+1}/{epochs} - "
                           f"TabGenLoss: {history['tab_gen_loss'][-1]:.4f}, "
                           f"TsGenLoss: {history['ts_gen_loss'][-1]:.4f}, "
                           f"CrossLoss: {history['cross_modal_loss'][-1]:.4f}")

        # Save final models
        self.save_models()
        logger.info("=" * 60)
        logger.info("[OK] GAN training completed successfully")
        logger.info(f"[OK] Models saved to: {MODEL_DIR}")
        logger.info("=" * 60)

        return history

    def save_models(self):
        """Save all GAN models with detailed logging."""
        os.makedirs(MODEL_DIR, exist_ok=True)
        
        model_files = {
            "tabular_generator.pth": self.tab_gen.state_dict(),
            "tabular_discriminator.pth": self.tab_disc.state_dict(),
            "timeseries_generator.pth": self.ts_gen.state_dict(),
            "timeseries_discriminator.pth": self.ts_disc.state_dict(),
            "cross_modal_generator.pth": self.cross_modal.state_dict()
        }
        
        for filename, state_dict in model_files.items():
            filepath = os.path.join(MODEL_DIR, filename)
            torch.save(state_dict, filepath)
            logger.info(f"[OK] Saved: {filepath}")

    def load_models(self):
        """Load all GAN models with proper device mapping and detailed logging."""
        try:
            # Check if model files exist
            model_files = [
                f"{MODEL_DIR}/tabular_generator.pth",
                f"{MODEL_DIR}/timeseries_generator.pth",
                f"{MODEL_DIR}/cross_modal_generator.pth"
            ]

            missing_files = [f for f in model_files if not os.path.exists(f)]
            if missing_files:
                logger.warning(f"[WARNING] GAN model files not found: {missing_files}")
                return False

            # Load with proper device mapping
            logger.info(f"Loading GAN models from: {MODEL_DIR}")
            
            self.tab_gen.load_state_dict(
                torch.load(f"{MODEL_DIR}/tabular_generator.pth", map_location=self.device)
            )
            self.tab_disc.load_state_dict(
                torch.load(f"{MODEL_DIR}/tabular_discriminator.pth", map_location=self.device)
            )
            self.ts_gen.load_state_dict(
                torch.load(f"{MODEL_DIR}/timeseries_generator.pth", map_location=self.device)
            )
            self.ts_disc.load_state_dict(
                torch.load(f"{MODEL_DIR}/timeseries_discriminator.pth", map_location=self.device)
            )
            self.cross_modal.load_state_dict(
                torch.load(f"{MODEL_DIR}/cross_modal_generator.pth", map_location=self.device)
            )

            # Set to evaluation mode
            self.tab_gen.eval()
            self.ts_gen.eval()
            self.cross_modal.eval()

            logger.info(f"[OK] GAN models loaded successfully from {MODEL_DIR}")
            return True

        except Exception as e:
            logger.error(f"[ERROR] Failed to load GAN models: {str(e)}")
            return False
