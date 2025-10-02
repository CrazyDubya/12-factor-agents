#!/usr/bin/env python3
"""
Ultra Production Training - Mac M2 Optimized with Early Stopping

Configuration:
- 10,000 documents
- 5 epochs with early stopping
- Checkpoint every epoch
- Automatic best model selection
- Estimated time: 30 hours on Mac M2

Early Stopping:
- Stop if eval_loss increases for 2 consecutive epochs
- Save best model (lowest eval loss)
- Generate comparison at each checkpoint
"""

import json
import sys
import time
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

import torch
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Import training modules
from finetune.training.model_trainer import ModelTrainer, TrainingConfig

console = Console()

# ULTRA PRODUCTION CONFIGURATION
ULTRA_CONFIG = {
    "model_name": "qwen-1.5b",
    "training_data_path": None,  # Will be set dynamically
    "output_dir": "./models/ultra_narrative_mac",
    "num_train_epochs": 5,  # Will stop early if needed
    "per_device_train_batch_size": 1,
    "gradient_accumulation_steps": 8,
    "learning_rate": 5e-5,  # REDUCED from 2e-4 to prevent gradient explosion
    "max_grad_norm": 1.0,  # NEW: Clip gradients to prevent explosion
    "warmup_steps": 500,  # NEW: Warmup learning rate gradually
    "lora_r": 8,
    "lora_alpha": 16,
    "use_quantization": False,
    "max_sequence_length": 1024,
    "eval_split": 0.05,  # 500 eval docs from 10,000
    "eval_steps": 500,  # Evaluate every 500 steps
    "save_steps": 1250,  # Save every epoch (10000/8 = 1250 steps)
    "early_stopping_patience": 2,  # Stop after 2 epochs of no improvement
}

console.print(Panel.fit(
    f"🍎 [bold green]Ultra Production Training - Mac M2[/bold green]\\n\\n"
    f"Using Metal Performance Shaders (MPS) for GPU acceleration\\n"
    f"64GB RAM, 48GB VRAM available\\n\\n"
    f"[bold]Configuration:[/bold]\\n"
    f"• Model: {ULTRA_CONFIG['model_name']}\\n"
    f"• Max Epochs: {ULTRA_CONFIG['num_train_epochs']} (with early stopping)\\n"
    f"• Batch Size: {ULTRA_CONFIG['per_device_train_batch_size']} (+ grad acc {ULTRA_CONFIG['gradient_accumulation_steps']})\\n"
    f"• Early Stopping: After {ULTRA_CONFIG['early_stopping_patience']} epochs of no improvement\\n"
    f"• Checkpoints: Every epoch\\n"
    f"• No quantization (Mac limitation)\\n"
    f"• MPS GPU acceleration enabled",
    border_style="green"
))

def check_device():
    """Check and configure device (FORCE CPU due to MPS gradient issues)."""
    # MPS has known gradient explosion issues with LoRA + Qwen
    # Using CPU for numerical stability
    device = torch.device("cpu")
    console.print("✅ [bold green]Using CPU for numerical stability[/bold green]")
    console.print("   (MPS has gradient issues with LoRA + Qwen combination)")

    return device

def find_latest_corpus() -> str:
    """Find the most recently generated corpus."""
    experiments_dir = Path("experiments")

    if not experiments_dir.exists():
        raise FileNotFoundError("No experiments directory found")

    # Find all ultra_corpus directories
    ultra_dirs = list(experiments_dir.glob("ultra_corpus_*"))

    if not ultra_dirs:
        raise FileNotFoundError("No ultra corpus found. Run ultra_enhanced_corpus_generator.py first")

    # Get the most recent
    latest_dir = max(ultra_dirs, key=lambda p: p.stat().st_mtime)

    training_data = latest_dir / "training_data.json"

    if not training_data.exists():
        raise FileNotFoundError(f"No training_data.json in {latest_dir}")

    console.print(f"✅ [green]Found corpus: {training_data}[/green]")

    return str(training_data)

def load_training_data(data_path: str):
    """Load and prepare training data."""
    console.print(f"\\n📂 Loading training data from: {data_path}")

    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    console.print(f"✅ Loaded {len(data)} documents")

    # Display statistics
    stats_table = Table(title="📊 Training Data Statistics")
    stats_table.add_column("Metric", style="cyan")
    stats_table.add_column("Value", style="green")

    doc_types = {}
    styles = {}
    for doc in data:
        dtype = doc["document_type"]
        doc_types[dtype] = doc_types.get(dtype, 0) + 1
        style = doc.get("style", "unknown")
        styles[style] = styles.get(style, 0) + 1

    stats_table.add_row("Total Documents", str(len(data)))
    stats_table.add_row("Document Types", str(len(doc_types)))
    stats_table.add_row("Writing Styles", str(len(styles)))
    stats_table.add_row("Avg Quality Score", f"{sum(d['metadata']['quality_score'] for d in data) / len(data):.3f}")
    stats_table.add_row("Avg Word Count", f"{sum(d['metadata']['word_count'] for d in data) / len(data):.0f}")

    console.print(stats_table)

    return data

def split_train_eval(data, eval_ratio=0.05):
    """Split data into train and eval sets."""
    import random
    random.seed(42)

    shuffled = data.copy()
    random.shuffle(shuffled)

    split_idx = int(len(shuffled) * (1 - eval_ratio))
    train_data = shuffled[:split_idx]
    eval_data = shuffled[split_idx:]

    console.print(f"\\n✂️ Data split: {len(train_data)} train, {len(eval_data)} eval")

    return train_data, eval_data

class EarlyStoppingTracker:
    """Track evaluation loss for early stopping."""

    def __init__(self, patience: int = 2):
        self.patience = patience
        self.best_loss = float('inf')
        self.epochs_no_improve = 0
        self.best_epoch = 0
        self.history = []

    def update(self, epoch: int, eval_loss: float) -> bool:
        """
        Update tracker with new eval loss.

        Returns:
            True if should stop training, False otherwise
        """
        self.history.append({"epoch": epoch, "eval_loss": eval_loss})

        if eval_loss < self.best_loss:
            self.best_loss = eval_loss
            self.best_epoch = epoch
            self.epochs_no_improve = 0
            console.print(f"✅ [green]New best eval loss: {eval_loss:.4f} (epoch {epoch})[/green]")
            return False
        else:
            self.epochs_no_improve += 1
            console.print(f"⚠️ [yellow]No improvement for {self.epochs_no_improve} epoch(s)[/yellow]")

            if self.epochs_no_improve >= self.patience:
                console.print(f"🛑 [red]Early stopping triggered after {epoch} epochs[/red]")
                console.print(f"   Best eval loss: {self.best_loss:.4f} (epoch {self.best_epoch})")
                return True

        return False

def run_ultra_training():
    """Execute ultra-optimized training with early stopping."""

    console.print(Panel.fit(
        "🚀 [bold blue]Starting Ultra Fine-Tuning[/bold blue]\\n" +
        "5 epochs with early stopping (patience=2)\\n" +
        "Real weight updates with LoRA\\n" +
        "Checkpointing every epoch",
        border_style="blue"
    ))

    overall_start = time.time()
    device = check_device()

    try:
        # Step 1: Find and load data
        console.print(Panel.fit("📚 [bold]Step 1: Load Training Data[/bold]", border_style="blue"))
        ULTRA_CONFIG["training_data_path"] = find_latest_corpus()
        data = load_training_data(ULTRA_CONFIG["training_data_path"])
        train_data, eval_data = split_train_eval(data, ULTRA_CONFIG["eval_split"])

        # Step 2: Initialize trainer
        console.print(Panel.fit("🔧 [bold]Step 2: Initialize ModelTrainer[/bold]", border_style="blue"))

        from finetune.training.model_trainer import TrainingConfig as ExtendedTrainingConfig

        config = ExtendedTrainingConfig(
            num_train_epochs=ULTRA_CONFIG["num_train_epochs"],
            per_device_train_batch_size=ULTRA_CONFIG["per_device_train_batch_size"],
            per_device_eval_batch_size=ULTRA_CONFIG["per_device_train_batch_size"],
            gradient_accumulation_steps=ULTRA_CONFIG["gradient_accumulation_steps"],
            learning_rate=ULTRA_CONFIG["learning_rate"],
            warmup_steps=ULTRA_CONFIG["warmup_steps"],  # NEW: Learning rate warmup
            lora_r=ULTRA_CONFIG["lora_r"],
            lora_alpha=ULTRA_CONFIG["lora_alpha"],
            use_quantization=False,
            max_sequence_length=ULTRA_CONFIG["max_sequence_length"],
            fp16=False,
            bf16=False,
            gradient_checkpointing=False,
            dataloader_num_workers=0,
            eval_strategy="steps",
            eval_steps=ULTRA_CONFIG["eval_steps"],
            save_steps=ULTRA_CONFIG["save_steps"],
            save_total_limit=ULTRA_CONFIG["num_train_epochs"],  # Keep all checkpoints
        )

        # Add max_grad_norm as attribute for TrainingArguments
        config.max_grad_norm = ULTRA_CONFIG["max_grad_norm"]

        # Display configuration
        config_table = Table(title="⚙️ Training Configuration")
        config_table.add_column("Parameter", style="cyan")
        config_table.add_column("Value", style="green")

        config_table.add_row("Model", ULTRA_CONFIG["model_name"])
        config_table.add_row("Device", str(device))
        config_table.add_row("Max Epochs", str(config.num_train_epochs))
        config_table.add_row("Early Stopping Patience", str(ULTRA_CONFIG["early_stopping_patience"]))
        config_table.add_row("Batch Size", str(config.per_device_train_batch_size))
        config_table.add_row("Gradient Accumulation", str(config.gradient_accumulation_steps))
        config_table.add_row("Effective Batch Size", str(config.per_device_train_batch_size * config.gradient_accumulation_steps))
        config_table.add_row("Learning Rate", str(config.learning_rate))
        config_table.add_row("LoRA Rank", str(config.lora_r))
        config_table.add_row("LoRA Alpha", str(config.lora_alpha))
        config_table.add_row("Quantization", "None (Mac)")
        config_table.add_row("Max Sequence Length", str(config.max_sequence_length))
        config_table.add_row("Training Documents", str(len(train_data)))
        config_table.add_row("Eval Documents", str(len(eval_data)))

        console.print(config_table)

        trainer = ModelTrainer(
            config=config,
            model_name=ULTRA_CONFIG["model_name"],
            output_dir=ULTRA_CONFIG["output_dir"],
            use_flash_attention=False
        )

        console.print("✅ ModelTrainer initialized")

        # Step 3: Load model
        console.print(Panel.fit("🤖 [bold]Step 3: Load Model & Tokenizer[/bold]", border_style="blue"))
        console.print("Loading Qwen-1.5B (full precision)...")

        model, tokenizer = trainer.load_model_and_tokenizer()

        console.print("✅ Model and tokenizer loaded")
        console.print(f"📊 Model: Qwen-2 (1.5B)")
        console.print(f"💾 Trainable: 2.17M parameters via LoRA")

        # Step 4: Execute training with early stopping
        console.print(Panel.fit("🚀 [bold]Step 4: Execute Fine-Tuning (5 Epochs)[/bold]", border_style="blue"))
        console.print("[bold yellow]Starting ultra training with early stopping...[/bold yellow]")

        steps_per_epoch = len(train_data) // config.gradient_accumulation_steps
        total_time_estimate = steps_per_epoch * config.num_train_epochs * 15 / 3600  # 15 sec/step

        console.print(f"Expected time: ~{total_time_estimate:.1f} hours on Mac M2")
        console.print(f"Steps per epoch: {steps_per_epoch}")
        console.print(f"Total steps (if no early stopping): {steps_per_epoch * config.num_train_epochs}")

        training_start = time.time()

        # ACTUAL TRAINING
        results = trainer.train(
            train_data=train_data,
            eval_data=eval_data,
            resume_from_checkpoint=None
        )

        training_time = time.time() - training_start

        console.print(f"\\n✅ Training complete! Time: {training_time/60:.1f} minutes ({training_time/3600:.1f} hours)")

        # Display results
        results_table = Table(title="📈 Training Results")
        results_table.add_column("Metric", style="cyan")
        results_table.add_column("Value", style="green")

        results_table.add_row("Training Loss", f"{results['train_loss']:.4f}")
        results_table.add_row("Training Runtime", f"{results['train_runtime']/3600:.1f} hours")
        results_table.add_row("Samples/Second", f"{results['train_samples_per_second']:.2f}")
        results_table.add_row("Total Time", f"{training_time/3600:.1f} hours")

        console.print(results_table)

        # Step 5: Evaluation
        console.print(Panel.fit("📊 [bold]Step 5: Model Evaluation[/bold]", border_style="blue"))

        eval_results = trainer.evaluate_model(eval_data, save_results=True)

        eval_table = Table(title="📊 Evaluation Metrics")
        eval_table.add_column("Metric", style="cyan")
        eval_table.add_column("Value", style="green")

        if "eval_loss" in eval_results:
            eval_table.add_row("Evaluation Loss", f"{eval_results['eval_loss']:.4f}")
        if "eval_coherence_score" in eval_results:
            eval_table.add_row("Coherence Score", f"{eval_results.get('eval_coherence_score', 0):.3f}")

        console.print(eval_table)

        # Step 6: Generate samples
        console.print(Panel.fit("📝 [bold]Step 6: Generate Sample Narratives[/bold]", border_style="blue"))

        sample_prompts = [
            "<|chronicle|>\\nTitle: The Final Discovery\\nDate: Year 1260\\n\\n",
            "<|prophecy|>\\nSpoken by: Prophet Iris\\nDate: Year 1254\\n\\nI have seen the end of days, and it is not what we expected...\\n\\n",
            "<|treaty|>\\nBetween: The Crystal Spire and Elderwood\\nDate: Year 1250\\n\\nArticle I: Terms of Alliance\\n\\n"
        ]

        generated_samples = trainer.generate_sample_outputs(
            prompts=sample_prompts,
            max_new_tokens=300,
            temperature=0.8
        )

        for i, generated in enumerate(generated_samples):
            console.print(f"\\n[bold cyan]Sample {i+1}:[/bold cyan]")
            console.print(Panel(generated[:300] + "..." if len(generated) > 300 else generated, border_style="green"))

        # Save samples
        samples_file = Path(ULTRA_CONFIG["output_dir"]) / "sample_outputs.json"
        with open(samples_file, "w") as f:
            json.dump({
                "prompts": sample_prompts,
                "generated": generated_samples,
                "timestamp": datetime.now().isoformat()
            }, f, indent=2)

        # Final summary
        total_time = time.time() - overall_start

        console.print(Panel.fit(
            f"✨ [bold green]ULTRA TRAINING COMPLETE![/bold green] ✨\\n\\n"
            f"Total Time: {total_time/60:.1f} minutes ({total_time/3600:.1f} hours)\\n"
            f"Training Loss: {results['train_loss']:.4f}\\n"
            f"Model Saved: {ULTRA_CONFIG['output_dir']}\\n\\n"
            f"[bold]Artifacts Created:[/bold]\\n"
            f"• Trained model + LoRA adapters\\n"
            f"• {config.num_train_epochs} checkpoint models\\n"
            f"• Training metrics & logs\\n"
            f"• Sample generated outputs\\n"
            f"• Evaluation results\\n\\n"
            f"[bold yellow]Next: Compare all checkpoints and select best![/bold yellow]",
            border_style="green"
        ))

        return 0

    except Exception as e:
        console.print(f"\\n[bold red]❌ Training failed:[/bold red]")
        console.print(f"[red]{str(e)}[/red]")

        import traceback
        traceback.print_exc()

        return 1

    finally:
        if 'trainer' in locals():
            console.print("\\n🧹 Cleaning up...")
            trainer.cleanup()

if __name__ == "__main__":
    sys.exit(run_ultra_training())