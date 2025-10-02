"""
Model Trainer with Parameter-Efficient Fine-Tuning

Implements comprehensive training pipeline with support for LoRA, QLoRA,
and other PEFT techniques optimized for narrative generation tasks.
"""

import json
import logging
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import torch
import torch.nn.functional as F
from peft import (
    LoraConfig,
    PeftModel,
    TaskType,
    get_peft_model,
    prepare_model_for_kbit_training,
)
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    DataCollatorForLanguageModeling,
    Trainer,
    TrainingArguments,
)
from transformers.trainer_callback import TrainerCallback

from ..config import SUPPORTED_MODELS, TrainingConfig as BaseTrainingConfig
from .dataset_manager import DatasetManager
from .evaluation_manager import EvaluationManager
from .training_utils import TrainingLogger, ModelSaver


@dataclass
class TrainingConfig(BaseTrainingConfig):
    """Extended training configuration with narrative-specific parameters."""

    # Core training parameters (compatible with transformers)
    num_train_epochs: int = 3
    per_device_train_batch_size: int = 4
    per_device_eval_batch_size: int = 4
    use_quantization: bool = True
    warmup_steps: int = 100
    lr_scheduler_type: str = "cosine"
    max_steps: int = -1
    lora_target_modules: list = None

    # Narrative-specific parameters
    max_sequence_length: int = 2048
    document_context_length: int = 1024
    cross_document_coherence_weight: float = 0.1
    temporal_consistency_weight: float = 0.05
    character_consistency_weight: float = 0.05

    # Advanced training parameters
    gradient_checkpointing: bool = True
    dataloader_num_workers: int = 4
    dataloader_pin_memory: bool = True
    fp16: bool = True
    bf16: bool = False

    # Evaluation parameters
    eval_steps: int = 100
    eval_strategy: str = "steps"
    eval_accumulation_steps: int = 1

    # Logging and saving
    logging_steps: int = 10
    save_steps: int = 500
    save_total_limit: int = 3

    def __post_init__(self):
        """Validate configuration and set derived parameters."""
        # Initialize default values
        if self.lora_target_modules is None:
            self.lora_target_modules = ["q_proj", "k_proj", "v_proj", "o_proj"]

        # Auto-detect bf16 capability
        if torch.cuda.is_available():
            device_capability = torch.cuda.get_device_capability()
            if device_capability[0] >= 8:  # A100, H100, RTX 40xx series
                self.bf16 = True
                self.fp16 = False

        # Adjust batch size for memory efficiency
        if self.use_quantization and self.per_device_train_batch_size > 2:
            logging.warning("Reducing batch size for quantized training")
            self.per_device_train_batch_size = 2


class NarrativeTrainerCallback(TrainerCallback):
    """Custom callback for narrative-specific training monitoring."""

    def __init__(self, trainer_instance: "ModelTrainer"):
        self.trainer_instance = trainer_instance
        self.best_coherence_score = 0.0

    def on_evaluate(self, args, state, control, model, logs=None, **kwargs):
        """Handle evaluation events with narrative metrics."""
        if logs and "eval_coherence_score" in logs:
            coherence_score = logs["eval_coherence_score"]
            if coherence_score > self.best_coherence_score:
                self.best_coherence_score = coherence_score
                # Save best model for coherence
                self.trainer_instance.save_best_model("coherence")


class ModelTrainer:
    """
    Advanced model trainer with parameter-efficient fine-tuning support.

    Features:
    - LoRA/QLoRA training with 4-bit quantization
    - Narrative coherence optimization
    - Multi-document consistency training
    - Advanced evaluation metrics
    - Efficient memory management
    """

    def __init__(
        self,
        config: TrainingConfig,
        model_name: str = "qwen-1.5b",
        output_dir: str = "./models",
        use_flash_attention: bool = True,
    ):
        self.config = config
        self.model_name = model_name
        self.output_dir = Path(output_dir)
        self.use_flash_attention = use_flash_attention

        # Initialize components
        self.logger = TrainingLogger(self.output_dir / "training_logs")
        self.model_saver = ModelSaver(self.output_dir)
        self.dataset_manager = DatasetManager()
        self.evaluation_manager = EvaluationManager()

        # Model components
        self.tokenizer = None
        self.model = None
        self.trainer = None

        # Training state
        self.training_history = []
        self.best_models = {}

        self._setup_directories()

    def _setup_directories(self):
        """Create necessary directories."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "checkpoints").mkdir(exist_ok=True)
        (self.output_dir / "best_models").mkdir(exist_ok=True)
        (self.output_dir / "evaluation_results").mkdir(exist_ok=True)

    def load_model_and_tokenizer(self) -> Tuple[AutoModelForCausalLM, AutoTokenizer]:
        """Load and prepare model and tokenizer with PEFT configuration."""

        if self.model_name not in SUPPORTED_MODELS:
            raise ValueError(f"Unsupported model: {self.model_name}")

        model_config = SUPPORTED_MODELS[self.model_name]
        self.logger.log(f"Loading model: {model_config.name} ({model_config.size})")

        # Tokenizer setup
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_config.model_id,
            trust_remote_code=True,
            padding_side="right",
        )

        # Add padding token if missing
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        # Quantization configuration
        bnb_config = None
        if self.config.use_quantization:
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.bfloat16 if self.config.bf16 else torch.float16,
                bnb_4bit_use_double_quant=True,
            )

        # Model loading
        model_kwargs = {
            "trust_remote_code": True,
            "torch_dtype": torch.bfloat16 if self.config.bf16 else torch.float16,
            "device_map": "auto",
        }

        if bnb_config:
            model_kwargs["quantization_config"] = bnb_config

        if self.use_flash_attention:
            model_kwargs["attn_implementation"] = "flash_attention_2"

        self.model = AutoModelForCausalLM.from_pretrained(
            model_config.model_id,
            **model_kwargs
        )

        # Prepare for PEFT training
        if self.config.use_quantization:
            self.model = prepare_model_for_kbit_training(self.model)

        # LoRA configuration
        lora_config = LoraConfig(
            r=self.config.lora_r,
            lora_alpha=self.config.lora_alpha,
            target_modules=self.config.lora_target_modules,
            lora_dropout=self.config.lora_dropout,
            bias="none",
            task_type=TaskType.CAUSAL_LM,
        )

        # Apply LoRA
        self.model = get_peft_model(self.model, lora_config)
        self.model.print_trainable_parameters()

        self.logger.log(f"Model loaded with {self.model.num_parameters()} total parameters")

        return self.model, self.tokenizer

    def prepare_datasets(
        self,
        train_data: List[Dict],
        eval_data: Optional[List[Dict]] = None,
        test_data: Optional[List[Dict]] = None,
    ) -> Dict:
        """Prepare datasets for training with narrative-specific preprocessing."""

        self.logger.log(f"Preparing datasets: {len(train_data)} train samples")

        # Convert to HuggingFace datasets
        datasets = self.dataset_manager.create_datasets(
            train_data=train_data,
            eval_data=eval_data,
            test_data=test_data,
            tokenizer=self.tokenizer,
            max_length=self.config.max_sequence_length,
        )

        self.logger.log("Datasets prepared successfully")
        return datasets

    def create_trainer(self, datasets: Dict) -> Trainer:
        """Create trainer with narrative-specific configuration."""

        # Training arguments
        training_args = TrainingArguments(
            output_dir=str(self.output_dir / "checkpoints"),
            per_device_train_batch_size=self.config.per_device_train_batch_size,
            per_device_eval_batch_size=self.config.per_device_eval_batch_size,
            gradient_accumulation_steps=self.config.gradient_accumulation_steps,
            learning_rate=self.config.learning_rate,
            lr_scheduler_type=self.config.lr_scheduler_type,
            warmup_steps=self.config.warmup_steps,
            max_grad_norm=getattr(self.config, 'max_grad_norm', 1.0),  # NEW: Gradient clipping
            num_train_epochs=self.config.num_train_epochs,
            max_steps=self.config.max_steps if self.config.max_steps > 0 else -1,
            eval_strategy=self.config.eval_strategy if hasattr(self.config, 'eval_strategy') else "no",
            eval_steps=self.config.eval_steps if hasattr(self.config, 'eval_steps') else None,
            logging_steps=self.config.logging_steps,
            save_steps=self.config.save_steps,
            save_total_limit=self.config.save_total_limit,
            load_best_model_at_end=False,
            dataloader_num_workers=self.config.dataloader_num_workers if hasattr(self.config, 'dataloader_num_workers') else 0,
            gradient_checkpointing=self.config.gradient_checkpointing if hasattr(self.config, 'gradient_checkpointing') else False,
            fp16=self.config.fp16 if hasattr(self.config, 'fp16') else False,
            bf16=self.config.bf16 if hasattr(self.config, 'bf16') else False,
            logging_dir=str(self.output_dir / "training_logs" / "tensorboard"),
            report_to=[],  # Disable reporting for Mac
            run_name=f"{self.model_name}_{int(time.time())}",
        )

        # Data collator for language modeling
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False,
            pad_to_multiple_of=8 if self.config.fp16 or self.config.bf16 else None,
        )

        # Create standard Trainer (compatible with all versions)
        self.trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=datasets["train"],
            eval_dataset=datasets.get("eval"),
            data_collator=data_collator,
        )

        # Add custom callback
        self.trainer.add_callback(NarrativeTrainerCallback(self))

        return self.trainer

    def train(
        self,
        train_data: List[Dict],
        eval_data: Optional[List[Dict]] = None,
        resume_from_checkpoint: Optional[str] = None,
    ) -> Dict:
        """
        Execute complete training pipeline.

        Args:
            train_data: Training examples as list of dicts
            eval_data: Optional evaluation examples
            resume_from_checkpoint: Path to checkpoint to resume from

        Returns:
            Training results and metrics
        """

        self.logger.log("Starting training pipeline")
        start_time = time.time()

        try:
            # Load model and tokenizer
            if self.model is None or self.tokenizer is None:
                self.load_model_and_tokenizer()

            # Prepare datasets
            datasets = self.prepare_datasets(train_data, eval_data)

            # Create trainer
            if self.trainer is None:
                self.create_trainer(datasets)

            # Execute training
            self.logger.log("Beginning model training")

            if resume_from_checkpoint:
                self.logger.log(f"Resuming from checkpoint: {resume_from_checkpoint}")

            train_result = self.trainer.train(resume_from_checkpoint=resume_from_checkpoint)

            # Save final model
            self.trainer.save_model()
            self.tokenizer.save_pretrained(self.trainer.args.output_dir)

            # Training summary
            training_time = time.time() - start_time

            results = {
                "train_runtime": train_result.metrics["train_runtime"],
                "train_samples_per_second": train_result.metrics["train_samples_per_second"],
                "train_loss": train_result.metrics["train_loss"],
                "total_training_time": training_time,
                "model_name": self.model_name,
                "config": self.config.__dict__,
            }

            # Save training results
            with open(self.output_dir / "training_results.json", "w") as f:
                json.dump(results, f, indent=2)

            self.logger.log(f"Training completed in {training_time:.2f} seconds")
            self.logger.log(f"Final training loss: {train_result.metrics['train_loss']:.4f}")

            return results

        except Exception as e:
            self.logger.log(f"Training failed with error: {str(e)}", level="ERROR")
            raise

    def evaluate_model(
        self,
        eval_data: List[Dict],
        save_results: bool = True,
    ) -> Dict:
        """
        Comprehensive model evaluation with narrative metrics.

        Args:
            eval_data: Evaluation examples
            save_results: Whether to save evaluation results

        Returns:
            Comprehensive evaluation metrics
        """

        self.logger.log("Starting model evaluation")

        if self.model is None or self.tokenizer is None:
            raise ValueError("Model not loaded. Call load_model_and_tokenizer() first.")

        # Evaluate with trainer
        eval_results = self.trainer.evaluate() if self.trainer else {}

        # Advanced narrative evaluation
        narrative_metrics = self.evaluation_manager.evaluate_narrative_quality(
            model=self.model,
            tokenizer=self.tokenizer,
            eval_data=eval_data,
            config=self.config,
        )

        # Combine results
        combined_results = {
            **eval_results,
            **narrative_metrics,
            "evaluation_timestamp": time.time(),
            "model_name": self.model_name,
        }

        if save_results:
            eval_file = self.output_dir / "evaluation_results" / f"eval_{int(time.time())}.json"
            with open(eval_file, "w") as f:
                json.dump(combined_results, f, indent=2)

        self.logger.log("Evaluation completed")
        return combined_results

    def save_best_model(self, metric_name: str):
        """Save model as best for specific metric."""
        if self.trainer:
            best_model_dir = self.output_dir / "best_models" / metric_name
            self.trainer.save_model(str(best_model_dir))
            self.tokenizer.save_pretrained(str(best_model_dir))
            self.best_models[metric_name] = str(best_model_dir)
            self.logger.log(f"Saved best model for {metric_name}")

    def generate_sample_outputs(
        self,
        prompts: List[str],
        max_new_tokens: int = 512,
        temperature: float = 0.8,
        top_p: float = 0.9,
        do_sample: bool = True,
    ) -> List[str]:
        """Generate sample outputs for qualitative evaluation."""

        if self.model is None or self.tokenizer is None:
            raise ValueError("Model not loaded")

        self.model.eval()
        generated_texts = []

        with torch.no_grad():
            for prompt in prompts:
                # Tokenize input
                inputs = self.tokenizer(
                    prompt,
                    return_tensors="pt",
                    padding=True,
                    truncation=True,
                    max_length=self.config.max_sequence_length - max_new_tokens,
                ).to(self.model.device)

                # Generate
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    do_sample=do_sample,
                    pad_token_id=self.tokenizer.eos_token_id,
                )

                # Decode
                generated_text = self.tokenizer.decode(
                    outputs[0][inputs["input_ids"].shape[1]:],
                    skip_special_tokens=True,
                )

                generated_texts.append(generated_text.strip())

        return generated_texts

    def cleanup(self):
        """Clean up resources and save final state."""
        if hasattr(self, 'trainer') and self.trainer:
            del self.trainer

        if hasattr(self, 'model') and self.model:
            del self.model

        torch.cuda.empty_cache()
        self.logger.log("Training resources cleaned up")


def create_training_config(**kwargs) -> TrainingConfig:
    """Factory function to create training configuration with sensible defaults."""
    return TrainingConfig(**kwargs)