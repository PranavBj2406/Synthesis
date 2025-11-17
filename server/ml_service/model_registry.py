
# import os
# import json
# import torch
# import logging
# from datetime import datetime
# from typing import Dict, Optional, Tuple
# from models import TimeSeriesGenerator, TabularGenerator, CrossModalGenerator
# from models import TimeSeriesDiscriminator, TabularDiscriminator
# from config import MODEL_DIR
# import re

# logger = logging.getLogger(__name__)

# class ModelRegistry:
#     def __init__(self):
#         self.ts_generator: Optional[TimeSeriesGenerator] = None
#         self.tab_generator: Optional[TabularGenerator] = None
#         self.cross_modal_generator: Optional[CrossModalGenerator] = None
#         self.ts_discriminator: Optional[TimeSeriesDiscriminator] = None
#         self.tab_discriminator: Optional[TabularDiscriminator] = None
#         self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
#         self.training_history: Dict = {}
#         self.is_trained = False

#     def initialize_models(self):
#         """Initialize all models."""
#         logger.info("Initializing models...")
#         self.ts_generator = TimeSeriesGenerator().to(self.device)
#         self.tab_generator = TabularGenerator().to(self.device)
#         self.cross_modal_generator = CrossModalGenerator().to(self.device)
#         self.ts_discriminator = TimeSeriesDiscriminator().to(self.device)
#         self.tab_discriminator = TabularDiscriminator().to(self.device)
#         logger.info(f"Models initialized on device: {self.device}")

#     def get_generators(self) -> Tuple[TimeSeriesGenerator, TabularGenerator, CrossModalGenerator]:
#         """Get generator models."""
#         if not self.is_trained:
#             raise RuntimeError("Models not trained. Please train models first.")
#         return self.ts_generator, self.tab_generator, self.cross_modal_generator

#     def get_discriminators(self) -> Tuple[TimeSeriesDiscriminator, TabularDiscriminator]:
#         """Get discriminator models."""
#         if not self.is_trained:
#             raise RuntimeError("Models not trained. Please train models first.")
#         return self.ts_discriminator, self.tab_discriminator

#     def save_models(self, epoch: int = None) -> str:
#         """Save all models and metadata."""
#         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
#         # Create model directory if it doesn't exist
#         os.makedirs(MODEL_DIR, exist_ok=True)
        
#         # Save model state dicts
#         model_files = {
#             'ts_generator': f"{MODEL_DIR}/ts_generator_{timestamp}.pt",
#             'tab_generator': f"{MODEL_DIR}/tab_generator_{timestamp}.pt",
#             'cross_modal_generator': f"{MODEL_DIR}/cross_modal_{timestamp}.pt",
#             'ts_discriminator': f"{MODEL_DIR}/ts_discriminator_{timestamp}.pt",
#             'tab_discriminator': f"{MODEL_DIR}/tab_discriminator_{timestamp}.pt"
#         }

#         torch.save(self.ts_generator.state_dict(), model_files['ts_generator'])
#         torch.save(self.tab_generator.state_dict(), model_files['tab_generator'])
#         torch.save(self.cross_modal_generator.state_dict(), model_files['cross_modal_generator'])
#         torch.save(self.ts_discriminator.state_dict(), model_files['ts_discriminator'])
#         torch.save(self.tab_discriminator.state_dict(), model_files['tab_discriminator'])

#         # Save metadata
#         metadata = {
#             'timestamp': timestamp,
#             'epoch': epoch,
#             'device': str(self.device),
#             'training_history': self.training_history,
#             'model_files': model_files
#         }

#         metadata_file = f"{MODEL_DIR}/metadata_{timestamp}.json"
#         with open(metadata_file, 'w') as f:
#             json.dump(metadata, f, indent=2)

#         logger.info(f"Models saved with timestamp: {timestamp}")
#         return timestamp

#     def load_models(self, timestamp: str = None) -> bool:
#         """Load models from checkpoint."""
#         try:
#             if timestamp is None:
#                 timestamp = self.get_latest_timestamp()
#                 if timestamp is None:
#                     logger.error("No saved models found")
#                     return False

#             logger.info(f"Loading models from timestamp: {timestamp}")

#             # Load metadata
#             metadata_file = f"{MODEL_DIR}/metadata_{timestamp}.json"
#             with open(metadata_file, 'r') as f:
#                 metadata = json.load(f)

#             # Initialize models if not already done
#             if self.ts_generator is None:
#                 self.initialize_models()

#             # Load model state dicts
#             self.ts_generator.load_state_dict(torch.load(f"{MODEL_DIR}/ts_generator_{timestamp}.pt", map_location=self.device))
#             self.tab_generator.load_state_dict(torch.load(f"{MODEL_DIR}/tab_generator_{timestamp}.pt", map_location=self.device))
#             self.cross_modal_generator.load_state_dict(torch.load(f"{MODEL_DIR}/cross_modal_{timestamp}.pt", map_location=self.device))

#             # Set to eval mode
#             self.ts_generator.eval()
#             self.tab_generator.eval()
#             self.cross_modal_generator.eval()

#             # Load training history
#             self.training_history = metadata.get('training_history', {})
#             self.is_trained = True

#             logger.info("Models loaded successfully")
#             return True

#         except Exception as e:
#             logger.error(f"Error loading models: {str(e)}")
#             return False

#     def get_latest_timestamp(self) -> Optional[str]:
#         """Get the latest timestamp from saved models."""
#         if not os.path.exists(MODEL_DIR):
#             return None

#         files = os.listdir(MODEL_DIR)
        
#         # Match full timestamp e.g., metadata_20250901_115537.json
#         timestamps = []
#         for f in files:
#             m = re.match(r"metadata_(\d{8}_\d{6})\.json", f)
#             if m:
#                 timestamps.append(m.group(1))

#         return max(timestamps) if timestamps else None

#     def set_training_history(self, history: Dict):
#         """Set training history."""
#         self.training_history = history
#         self.is_trained = True

#     def get_training_history(self) -> Dict:
#         """Get training history."""
#         return self.training_history

# # Global model registry instance
# model_registry = ModelRegistry()
import os
import json
import torch
import logging
from datetime import datetime
from typing import Dict, Optional, Tuple
from models import TimeSeriesGenerator, TabularGenerator, CrossModalGenerator
from models import TimeSeriesDiscriminator, TabularDiscriminator
from config import MODEL_DIR
import re

logger = logging.getLogger(__name__)

class ModelRegistry:
    def __init__(self):
        self.ts_generator: Optional[TimeSeriesGenerator] = None
        self.tab_generator: Optional[TabularGenerator] = None
        self.cross_modal_generator: Optional[CrossModalGenerator] = None
        self.ts_discriminator: Optional[TimeSeriesDiscriminator] = None
        self.tab_discriminator: Optional[TabularDiscriminator] = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.training_history: Dict = {}
        self.is_trained = False

    def initialize_models(self):
        """Initialize all models."""
        logger.info("Initializing models...")
        self.ts_generator = TimeSeriesGenerator().to(self.device)
        self.tab_generator = TabularGenerator().to(self.device)
        self.cross_modal_generator = CrossModalGenerator().to(self.device)
        self.ts_discriminator = TimeSeriesDiscriminator().to(self.device)
        self.tab_discriminator = TabularDiscriminator().to(self.device)
        logger.info(f"Models initialized on device: {self.device}")

    def get_generators(self) -> Tuple[TimeSeriesGenerator, TabularGenerator, CrossModalGenerator]:
        """Get generator models."""
        if not self.is_trained:
            raise RuntimeError("Models not trained. Please train models first.")
        return self.ts_generator, self.tab_generator, self.cross_modal_generator

    def get_discriminators(self) -> Tuple[TimeSeriesDiscriminator, TabularDiscriminator]:
        """Get discriminator models."""
        if not self.is_trained:
            raise RuntimeError("Models not trained. Please train models first.")
        return self.ts_discriminator, self.tab_discriminator

    def save_models(self, epoch: int = None) -> str:
        """Save all models and metadata."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create model directory if it doesn't exist
        os.makedirs(MODEL_DIR, exist_ok=True)
        
        # Save model state dicts
        model_files = {
            'ts_generator': f"{MODEL_DIR}/ts_generator_{timestamp}.pt",
            'tab_generator': f"{MODEL_DIR}/tab_generator_{timestamp}.pt",
            'cross_modal_generator': f"{MODEL_DIR}/cross_modal_{timestamp}.pt",
            'ts_discriminator': f"{MODEL_DIR}/ts_discriminator_{timestamp}.pt",
            'tab_discriminator': f"{MODEL_DIR}/tab_discriminator_{timestamp}.pt"
        }

        torch.save(self.ts_generator.state_dict(), model_files['ts_generator'])
        torch.save(self.tab_generator.state_dict(), model_files['tab_generator'])
        torch.save(self.cross_modal_generator.state_dict(), model_files['cross_modal_generator'])
        torch.save(self.ts_discriminator.state_dict(), model_files['ts_discriminator'])
        torch.save(self.tab_discriminator.state_dict(), model_files['tab_discriminator'])

        # Save metadata
        metadata = {
            'timestamp': timestamp,
            'epoch': epoch,
            'device': str(self.device),
            'training_history': self.training_history,
            'model_files': model_files
        }

        metadata_file = f"{MODEL_DIR}/metadata_{timestamp}.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"Models saved with timestamp: {timestamp}")
        return timestamp

    def load_models(self, timestamp: str = None) -> bool:
        """Load models from checkpoint."""
        try:
            if timestamp is None:
                timestamp = self.get_latest_timestamp()
                if timestamp is None:
                    logger.error("No saved models found")
                    return False

            logger.info(f"Loading models from timestamp: {timestamp}")

            # Load metadata
            metadata_file = f"{MODEL_DIR}/metadata_{timestamp}.json"
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)

            # Initialize models if not already done
            if self.ts_generator is None:
                self.initialize_models()

            # Load model state dicts
            self.ts_generator.load_state_dict(torch.load(f"{MODEL_DIR}/ts_generator_{timestamp}.pt", map_location=self.device))
            self.tab_generator.load_state_dict(torch.load(f"{MODEL_DIR}/tab_generator_{timestamp}.pt", map_location=self.device))
            self.cross_modal_generator.load_state_dict(torch.load(f"{MODEL_DIR}/cross_modal_{timestamp}.pt", map_location=self.device))

            # Set to eval mode
            self.ts_generator.eval()
            self.tab_generator.eval()
            self.cross_modal_generator.eval()

            # Load training history
            self.training_history = metadata.get('training_history', {})
            self.is_trained = True

            logger.info("Models loaded successfully")
            return True

        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
            return False

    def get_latest_timestamp(self) -> Optional[str]:
        """Get the latest timestamp from saved models."""
        if not os.path.exists(MODEL_DIR):
            return None

        files = os.listdir(MODEL_DIR)
        
        # Match full timestamp e.g., metadata_20250901_115537.json
        timestamps = []
        for f in files:
            m = re.match(r"metadata_(\d{8}_\d{6})\.json", f)
            if m:
                timestamps.append(m.group(1))

        return max(timestamps) if timestamps else None

    def set_training_history(self, history: Dict):
        """Set training history."""
        self.training_history = history
        self.is_trained = True

    def get_training_history(self) -> Dict:
        """Get training history."""
        return self.training_history

# Global model registry instance
model_registry = ModelRegistry()
