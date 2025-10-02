"""
Training Utilities and Helper Classes

Provides utility classes for model saving, logging, metrics tracking,
and other training-related functionality.
"""

import json
import logging
import os
import shutil
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import torch
import torch.nn as nn
from transformers import AutoTokenizer
from transformers.trainer_callback import TrainerCallback
from transformers.training_args import TrainingArguments

try:
    import wandb
    WANDB_AVAILABLE = True
except ImportError:
    WANDB_AVAILABLE = False

try:
    from tensorboardX import SummaryWriter
    TENSORBOARD_AVAILABLE = True
except ImportError:
    TENSORBOARD_AVAILABLE = False


class TrainingLogger:
    """
    Enhanced logging utility for training processes.

    Features:
    - Multi-level logging (file + console)
    - Metrics tracking and visualization
    - Integration with wandb and tensorboard
    - Training progress monitoring
    """

    def __init__(
        self,
        log_dir: Union[str, Path],
        experiment_name: Optional[str] = None,
        use_wandb: bool = False,
        use_tensorboard: bool = True,
        log_level: str = "INFO",
    ):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.experiment_name = experiment_name or f"training_{int(time.time())}"
        self.use_wandb = use_wandb and WANDB_AVAILABLE
        self.use_tensorboard = use_tensorboard and TENSORBOARD_AVAILABLE

        # Setup logging
        self._setup_logging(log_level)

        # Initialize tracking
        self.metrics_history = []
        self.start_time = time.time()

        # Setup external loggers
        self._setup_external_loggers()

    def _setup_logging(self, log_level: str):
        """Setup file and console logging."""
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # Setup logger
        self.logger = logging.getLogger(f"training_{self.experiment_name}")
        self.logger.setLevel(getattr(logging, log_level.upper()))

        # File handler
        log_file = self.log_dir / f"{self.experiment_name}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def _setup_external_loggers(self):
        """Setup wandb and tensorboard if available."""
        # Wandb
        self.wandb_run = None
        if self.use_wandb:
            try:
                self.wandb_run = wandb.init(
                    project="narrative-finetuning",
                    name=self.experiment_name,
                    dir=str(self.log_dir),
                )
                self.logger.info("Wandb logging initialized")
            except Exception as e:
                self.logger.warning(f"Wandb initialization failed: {e}")
                self.use_wandb = False

        # Tensorboard
        self.tensorboard_writer = None
        if self.use_tensorboard:
            try:
                tb_dir = self.log_dir / "tensorboard"
                self.tensorboard_writer = SummaryWriter(str(tb_dir))
                self.logger.info("Tensorboard logging initialized")
            except Exception as e:
                self.logger.warning(f"Tensorboard initialization failed: {e}")
                self.use_tensorboard = False

    def log(self, message: str, level: str = "INFO"):
        """Log a message."""
        log_func = getattr(self.logger, level.lower(), self.logger.info)
        log_func(message)

    def log_metrics(self, metrics: Dict[str, Any], step: Optional[int] = None):
        """Log metrics to all configured backends."""
        timestamp = time.time()

        # Add to history
        metric_entry = {
            "timestamp": timestamp,
            "step": step,
            "metrics": metrics.copy(),
        }
        self.metrics_history.append(metric_entry)

        # Log to file
        self.logger.info(f"Step {step}: {metrics}")

        # Log to wandb
        if self.use_wandb and self.wandb_run:
            try:
                self.wandb_run.log(metrics, step=step)
            except Exception as e:
                self.logger.warning(f"Wandb logging failed: {e}")

        # Log to tensorboard
        if self.use_tensorboard and self.tensorboard_writer:
            try:
                for key, value in metrics.items():
                    if isinstance(value, (int, float)):
                        self.tensorboard_writer.add_scalar(key, value, step or 0)
            except Exception as e:
                self.logger.warning(f"Tensorboard logging failed: {e}")

    def log_hyperparameters(self, config: Dict[str, Any]):
        """Log hyperparameters."""
        self.logger.info(f"Hyperparameters: {json.dumps(config, indent=2)}")

        if self.use_wandb and self.wandb_run:
            try:
                self.wandb_run.config.update(config)
            except Exception as e:
                self.logger.warning(f"Wandb config logging failed: {e}")

    def save_metrics(self):
        """Save metrics history to file."""
        metrics_file = self.log_dir / f"{self.experiment_name}_metrics.json"
        with open(metrics_file, "w") as f:
            json.dump(self.metrics_history, f, indent=2)

    def get_training_time(self) -> float:
        """Get total training time in seconds."""
        return time.time() - self.start_time

    def close(self):
        """Close all loggers and save final state."""
        self.save_metrics()

        if self.use_wandb and self.wandb_run:
            try:
                self.wandb_run.finish()
            except Exception as e:
                self.logger.warning(f"Wandb close failed: {e}")

        if self.use_tensorboard and self.tensorboard_writer:
            try:
                self.tensorboard_writer.close()
            except Exception as e:
                self.logger.warning(f"Tensorboard close failed: {e}")

        self.logger.info("Training logger closed")


class ModelSaver:
    """
    Advanced model saving utility with versioning and metadata.

    Features:
    - Automatic versioning
    - Metadata tracking
    - Best model management
    - Checkpoint cleanup
    """

    def __init__(
        self,
        save_dir: Union[str, Path],
        max_checkpoints: int = 5,
        save_optimizer: bool = True,
    ):
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)

        self.max_checkpoints = max_checkpoints
        self.save_optimizer = save_optimizer

        # Track saved models
        self.saved_models = []
        self.best_models = {}

    def save_checkpoint(
        self,
        model: nn.Module,
        tokenizer: AutoTokenizer,
        optimizer: Optional[torch.optim.Optimizer] = None,
        scheduler: Optional[Any] = None,
        step: int = 0,
        metrics: Optional[Dict[str, Any]] = None,
        is_best: bool = False,
        checkpoint_name: Optional[str] = None,
    ) -> str:
        """
        Save model checkpoint with metadata.

        Returns:
            Path to saved checkpoint
        """

        # Generate checkpoint name
        if checkpoint_name:
            checkpoint_dir = self.save_dir / checkpoint_name
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            checkpoint_dir = self.save_dir / f"checkpoint_step_{step}_{timestamp}"

        checkpoint_dir.mkdir(parents=True, exist_ok=True)

        try:
            # Save model and tokenizer
            model.save_pretrained(checkpoint_dir)
            tokenizer.save_pretrained(checkpoint_dir)

            # Save optimizer and scheduler if requested
            if self.save_optimizer and optimizer:
                torch.save(
                    optimizer.state_dict(),
                    checkpoint_dir / "optimizer.pt"
                )

            if scheduler:
                torch.save(
                    scheduler.state_dict(),
                    checkpoint_dir / "scheduler.pt"
                )

            # Save metadata
            metadata = {
                "step": step,
                "timestamp": time.time(),
                "datetime": datetime.now().isoformat(),
                "metrics": metrics or {},
                "is_best": is_best,
                "model_type": getattr(model, '__class__', {}).get('__name__', 'unknown'),
            }

            with open(checkpoint_dir / "metadata.json", "w") as f:
                json.dump(metadata, f, indent=2)

            # Track saved checkpoint
            checkpoint_info = {
                "path": str(checkpoint_dir),
                "step": step,
                "timestamp": time.time(),
                "is_best": is_best,
                "metrics": metrics or {},
            }
            self.saved_models.append(checkpoint_info)

            # Cleanup old checkpoints
            self._cleanup_old_checkpoints()

            logging.info(f"Checkpoint saved: {checkpoint_dir}")
            return str(checkpoint_dir)

        except Exception as e:
            logging.error(f"Failed to save checkpoint: {e}")
            # Cleanup partial checkpoint
            if checkpoint_dir.exists():
                shutil.rmtree(checkpoint_dir)
            raise

    def save_best_model(
        self,
        model: nn.Module,
        tokenizer: AutoTokenizer,
        metric_name: str,
        metric_value: float,
        step: int = 0,
        is_higher_better: bool = True,
    ) -> bool:
        """
        Save model if it's the best for given metric.

        Returns:
            True if model was saved as best
        """

        current_best = self.best_models.get(metric_name, {})

        # Check if this is the best
        if not current_best:
            is_new_best = True
        else:
            current_value = current_best.get("value", 0)
            if is_higher_better:
                is_new_best = metric_value > current_value
            else:
                is_new_best = metric_value < current_value

        if is_new_best:
            # Save as best model
            best_dir = self.save_dir / "best_models" / metric_name
            checkpoint_path = self.save_checkpoint(
                model=model,
                tokenizer=tokenizer,
                step=step,
                metrics={metric_name: metric_value},
                is_best=True,
                checkpoint_name=f"best_models/{metric_name}",
            )

            # Update best models tracking
            self.best_models[metric_name] = {
                "path": checkpoint_path,
                "value": metric_value,
                "step": step,
                "timestamp": time.time(),
            }

            logging.info(f"New best model for {metric_name}: {metric_value}")
            return True

        return False

    def _cleanup_old_checkpoints(self):
        """Remove old checkpoints to save space."""
        if len(self.saved_models) <= self.max_checkpoints:
            return

        # Sort by timestamp
        sorted_models = sorted(self.saved_models, key=lambda x: x["timestamp"])

        # Remove oldest checkpoints (but keep best models)
        while len(sorted_models) > self.max_checkpoints:
            oldest = sorted_models.pop(0)

            # Don't delete best models
            if oldest.get("is_best", False):
                continue

            # Delete checkpoint directory
            checkpoint_path = Path(oldest["path"])
            if checkpoint_path.exists():
                try:
                    shutil.rmtree(checkpoint_path)
                    logging.info(f"Removed old checkpoint: {checkpoint_path}")
                except Exception as e:
                    logging.warning(f"Failed to remove checkpoint {checkpoint_path}: {e}")

            # Remove from tracking
            self.saved_models.remove(oldest)

    def load_checkpoint(
        self,
        checkpoint_path: Union[str, Path],
        model: Optional[nn.Module] = None,
        optimizer: Optional[torch.optim.Optimizer] = None,
        scheduler: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """
        Load checkpoint and restore state.

        Returns:
            Metadata from checkpoint
        """

        checkpoint_path = Path(checkpoint_path)

        if not checkpoint_path.exists():
            raise FileNotFoundError(f"Checkpoint not found: {checkpoint_path}")

        # Load metadata
        metadata_file = checkpoint_path / "metadata.json"
        if metadata_file.exists():
            with open(metadata_file, "r") as f:
                metadata = json.load(f)
        else:
            metadata = {}

        # Load optimizer state
        if optimizer and self.save_optimizer:
            optimizer_file = checkpoint_path / "optimizer.pt"
            if optimizer_file.exists():
                try:
                    optimizer.load_state_dict(torch.load(optimizer_file))
                    logging.info("Optimizer state loaded")
                except Exception as e:
                    logging.warning(f"Failed to load optimizer state: {e}")

        # Load scheduler state
        if scheduler:
            scheduler_file = checkpoint_path / "scheduler.pt"
            if scheduler_file.exists():
                try:
                    scheduler.load_state_dict(torch.load(scheduler_file))
                    logging.info("Scheduler state loaded")
                except Exception as e:
                    logging.warning(f"Failed to load scheduler state: {e}")

        logging.info(f"Checkpoint loaded: {checkpoint_path}")
        return metadata

    def get_best_model_path(self, metric_name: str) -> Optional[str]:
        """Get path to best model for given metric."""
        best_info = self.best_models.get(metric_name)
        return best_info["path"] if best_info else None

    def list_checkpoints(self) -> List[Dict]:
        """List all saved checkpoints with metadata."""
        return self.saved_models.copy()

    def get_checkpoint_info(self) -> Dict:
        """Get comprehensive checkpoint information."""
        return {
            "total_checkpoints": len(self.saved_models),
            "best_models": self.best_models.copy(),
            "recent_checkpoints": self.saved_models[-5:] if self.saved_models else [],
            "save_dir": str(self.save_dir),
        }


class TrainingUtils:
    """
    Collection of training utility functions.
    """

    @staticmethod
    def calculate_model_size(model: nn.Module) -> Dict[str, int]:
        """Calculate model size information."""
        total_params = sum(p.numel() for p in model.parameters())
        trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)

        return {
            "total_parameters": total_params,
            "trainable_parameters": trainable_params,
            "frozen_parameters": total_params - trainable_params,
            "trainable_percentage": (trainable_params / total_params) * 100 if total_params > 0 else 0,
        }

    @staticmethod
    def estimate_memory_usage(
        model: nn.Module,
        batch_size: int = 1,
        sequence_length: int = 512,
        dtype: torch.dtype = torch.float16,
    ) -> Dict[str, float]:
        """Estimate GPU memory usage for training."""

        # Model parameters
        param_memory = sum(p.numel() for p in model.parameters()) * 4  # Assume float32 for params

        # Activations (rough estimate)
        hidden_size = getattr(model.config, 'hidden_size', 4096)
        activation_memory = batch_size * sequence_length * hidden_size * 4  # float32

        # Gradients
        gradient_memory = param_memory

        # Optimizer states (Adam: 2x parameters)
        optimizer_memory = param_memory * 2

        # Convert to MB
        total_memory_mb = (param_memory + activation_memory + gradient_memory + optimizer_memory) / (1024 * 1024)

        return {
            "parameters_mb": param_memory / (1024 * 1024),
            "activations_mb": activation_memory / (1024 * 1024),
            "gradients_mb": gradient_memory / (1024 * 1024),
            "optimizer_mb": optimizer_memory / (1024 * 1024),
            "total_mb": total_memory_mb,
            "total_gb": total_memory_mb / 1024,
        }

    @staticmethod
    def get_device_info() -> Dict[str, Any]:
        """Get information about available devices."""
        info = {
            "cuda_available": torch.cuda.is_available(),
            "cuda_device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
        }

        if torch.cuda.is_available():
            info["cuda_devices"] = []
            for i in range(torch.cuda.device_count()):
                device_info = {
                    "id": i,
                    "name": torch.cuda.get_device_name(i),
                    "memory_total": torch.cuda.get_device_properties(i).total_memory,
                    "memory_reserved": torch.cuda.memory_reserved(i),
                    "memory_allocated": torch.cuda.memory_allocated(i),
                }
                info["cuda_devices"].append(device_info)

        return info

    @staticmethod
    def create_training_summary(
        config: Dict[str, Any],
        model_info: Dict[str, Any],
        training_results: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Create comprehensive training summary."""

        return {
            "training_summary": {
                "start_time": datetime.now().isoformat(),
                "configuration": config,
                "model_information": model_info,
                "training_results": training_results,
                "system_info": TrainingUtils.get_device_info(),
            }
        }


class MetricsTracker:
    """Simple metrics tracking utility."""

    def __init__(self):
        self.metrics = {}
        self.history = []

    def update(self, metrics: Dict[str, float], step: int):
        """Update metrics."""
        self.metrics.update(metrics)
        entry = {"step": step, "timestamp": time.time(), **metrics}
        self.history.append(entry)

    def get_best(self, metric_name: str, higher_better: bool = True) -> Optional[Dict]:
        """Get best value for a metric."""
        if not self.history:
            return None

        if higher_better:
            best_entry = max(
                (entry for entry in self.history if metric_name in entry),
                key=lambda x: x[metric_name],
                default=None
            )
        else:
            best_entry = min(
                (entry for entry in self.history if metric_name in entry),
                key=lambda x: x[metric_name],
                default=None
            )

        return best_entry

    def get_latest(self) -> Dict:
        """Get latest metrics."""
        return self.history[-1] if self.history else {}

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "current_metrics": self.metrics.copy(),
            "history": self.history.copy(),
        }