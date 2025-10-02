#!/usr/bin/env python3
"""
Production Training Pipeline - Mac M2 Optimized

Uses Metal Performance Shaders (MPS) for GPU acceleration on Apple Silicon.
Runs without quantization since bitsandbytes is not available on macOS.

Requirements:
- Mac M2/M3 with sufficient RAM (32GB+)
- PyTorch with MPS support
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
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

# Import training modules
from finetune.training.model_trainer import ModelTrainer, TrainingConfig
from finetune.config import SUPPORTED_MODELS

console = Console()

# Mac M2 Optimized Configuration
PRODUCTION_CONFIG = {
    "model_name": "qwen-1.5b",
    "training_data_path": "experiments/extensive_1759206645/training_data.json",
    "output_dir": "./models/production_narrative_mac",
    "num_train_epochs": 3,  # Reduced for Mac (memory consideration)
    "per_device_train_batch_size": 1,  # Small batch for Mac
    "gradient_accumulation_steps": 8,  # Effective batch = 8
    "learning_rate": 2e-4,
    "lora_r": 8,  # Reduced rank for memory
    "lora_alpha": 16,
    "use_quantization": False,  # No quantization on Mac
    "max_sequence_length": 1024,  # Reduced for memory
    "eval_split": 0.05,  # Smaller eval set (100 docs)
}

console.print(Panel.fit(
    f"🍎 [bold green]Mac M2 Production Training[/bold green]\n\n"
    f"Using Metal Performance Shaders (MPS) for GPU acceleration\n"
    f"64GB RAM, 48GB VRAM available\n\n"
    f"[bold]Configuration:[/bold]\n"
    f"• Model: {PRODUCTION_CONFIG['model_name']}\n"
    f"• Epochs: {PRODUCTION_CONFIG['num_train_epochs']}\n"
    f"• Batch Size: {PRODUCTION_CONFIG['per_device_train_batch_size']} (+ grad acc {PRODUCTION_CONFIG['gradient_accumulation_steps']})\n"
    f"• No quantization (Mac limitation)\n"
    f"• MPS GPU acceleration enabled",
    border_style="green"
))

def check_device():
    """Check and configure device (MPS on Mac)."""
    if torch.backends.mps.is_available():
        device = torch.device("mps")
        console.print("✅ [bold green]MPS (Metal) GPU available[/bold green]")
        console.print(f"   Using Apple Silicon GPU acceleration")
    elif torch.cuda.is_available():
        device = torch.device("cuda")
        console.print("✅ [bold green]CUDA GPU available[/bold green]")
    else:
        device = torch.device("cpu")
        console.print("⚠️ [yellow]Using CPU (slower)[/yellow]")

    return device

def load_training_data(data_path: str):
    """Load and prepare training data."""
    console.print(f"\n📂 Loading training data from: {data_path}")

    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    console.print(f"✅ Loaded {len(data)} documents")

    # Display statistics
    stats_table = Table(title="📊 Training Data Statistics")
    stats_table.add_column("Metric", style="cyan")
    stats_table.add_column("Value", style="green")

    doc_types = {}
    for doc in data:
        dtype = doc["document_type"]
        doc_types[dtype] = doc_types.get(dtype, 0) + 1

    stats_table.add_row("Total Documents", str(len(data)))
    stats_table.add_row("Document Types", str(len(doc_types)))
    stats_table.add_row("Avg Quality Score", f"{sum(d['metadata']['quality_score'] for d in data) / len(data):.3f}")

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

    console.print(f"\n✂️ Data split: {len(train_data)} train, {len(eval_data)} eval")

    return train_data, eval_data

def run_mac_training():
    """Execute Mac-optimized training."""

    console.print(Panel.fit(
        "🚀 [bold blue]Starting Mac M2 Fine-Tuning[/bold blue]\n" +
        "Real weight updates with LoRA (no quantization)",
        border_style="blue"
    ))

    overall_start = time.time()
    device = check_device()

    try:
        # Step 1: Load data
        console.print(Panel.fit("📚 [bold]Step 1: Load Training Data[/bold]", border_style="blue"))
        data = load_training_data(PRODUCTION_CONFIG["training_data_path"])
        train_data, eval_data = split_train_eval(data, PRODUCTION_CONFIG["eval_split"])

        # Step 2: Initialize trainer
        console.print(Panel.fit("🔧 [bold]Step 2: Initialize ModelTrainer[/bold]", border_style="blue"))

        from finetune.training.model_trainer import TrainingConfig as ExtendedTrainingConfig

        config = ExtendedTrainingConfig(
            num_train_epochs=PRODUCTION_CONFIG["num_train_epochs"],
            per_device_train_batch_size=PRODUCTION_CONFIG["per_device_train_batch_size"],
            per_device_eval_batch_size=PRODUCTION_CONFIG["per_device_train_batch_size"],
            gradient_accumulation_steps=PRODUCTION_CONFIG["gradient_accumulation_steps"],
            learning_rate=PRODUCTION_CONFIG["learning_rate"],
            lora_r=PRODUCTION_CONFIG["lora_r"],
            lora_alpha=PRODUCTION_CONFIG["lora_alpha"],
            use_quantization=False,  # No quantization on Mac
            max_sequence_length=PRODUCTION_CONFIG["max_sequence_length"],
            fp16=False,  # MPS doesn't support fp16
            bf16=False,
            gradient_checkpointing=False,  # Disable for Mac compatibility
            dataloader_num_workers=0,  # Disable to avoid fork issues
        )

        # Display configuration
        config_table = Table(title="⚙️ Training Configuration")
        config_table.add_column("Parameter", style="cyan")
        config_table.add_column("Value", style="green")

        config_table.add_row("Model", PRODUCTION_CONFIG["model_name"])
        config_table.add_row("Device", str(device))
        config_table.add_row("Epochs", str(config.num_train_epochs))
        config_table.add_row("Batch Size", str(config.per_device_train_batch_size))
        config_table.add_row("Gradient Accumulation", str(config.gradient_accumulation_steps))
        config_table.add_row("Effective Batch Size", str(config.per_device_train_batch_size * config.gradient_accumulation_steps))
        config_table.add_row("Learning Rate", str(config.learning_rate))
        config_table.add_row("LoRA Rank", str(config.lora_r))
        config_table.add_row("LoRA Alpha", str(config.lora_alpha))
        config_table.add_row("Quantization", "None (Mac)")
        config_table.add_row("Max Sequence Length", str(config.max_sequence_length))

        console.print(config_table)

        trainer = ModelTrainer(
            config=config,
            model_name=PRODUCTION_CONFIG["model_name"],
            output_dir=PRODUCTION_CONFIG["output_dir"],
            use_flash_attention=False  # Not supported on Mac
        )

        console.print("✅ ModelTrainer initialized")

        # Step 3: Load model
        console.print(Panel.fit("🤖 [bold]Step 3: Load Model & Tokenizer[/bold]", border_style="blue"))
        console.print("Loading Qwen-1.5B (full precision)...")

        model, tokenizer = trainer.load_model_and_tokenizer()

        console.print("✅ Model and tokenizer loaded")
        console.print(f"📊 Model: {SUPPORTED_MODELS[PRODUCTION_CONFIG['model_name']].name}")
        console.print(f"💾 Size: {SUPPORTED_MODELS[PRODUCTION_CONFIG['model_name']].size}")

        # Step 4: Execute training
        console.print(Panel.fit("🚀 [bold]Step 4: Execute Fine-Tuning[/bold]", border_style="blue"))
        console.print("[bold yellow]Starting actual model training...[/bold yellow]")
        console.print(f"Expected time: ~2-4 hours on Mac M2")
        console.print(f"Training samples: {len(train_data)}")
        console.print(f"Validation samples: {len(eval_data)}")

        training_start = time.time()

        # ACTUAL TRAINING
        results = trainer.train(
            train_data=train_data,
            eval_data=eval_data,
            resume_from_checkpoint=None
        )

        training_time = time.time() - training_start

        console.print(f"\n✅ Training complete! Time: {training_time/60:.1f} minutes")

        # Display results
        results_table = Table(title="📈 Training Results")
        results_table.add_column("Metric", style="cyan")
        results_table.add_column("Value", style="green")

        results_table.add_row("Training Loss", f"{results['train_loss']:.4f}")
        results_table.add_row("Training Runtime", f"{results['train_runtime']:.1f}s")
        results_table.add_row("Samples/Second", f"{results['train_samples_per_second']:.2f}")
        results_table.add_row("Total Time", f"{training_time/60:.1f} min")

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
            "<|chronicle|>\nTitle: The Discovery at Dawn\nDate: Year 1245, Third Moon\n\n",
            "<|diary_entry|>\nAuthor: Chronicler Aria\nDate: Personal Record, Day 500\n\nDear Journal,\n\n",
            "<|letter|>\nFrom: Ambassador Kael\nTo: Archmage Lysander\n\nEsteemed Archmage,\n\n"
        ]

        generated_samples = trainer.generate_sample_outputs(
            prompts=sample_prompts,
            max_new_tokens=200,
            temperature=0.8
        )

        for i, generated in enumerate(generated_samples):
            console.print(f"\n[bold cyan]Sample {i+1}:[/bold cyan]")
            console.print(Panel(generated[:250] + "...", border_style="green"))

        # Save samples
        samples_file = Path(PRODUCTION_CONFIG["output_dir"]) / "sample_outputs.json"
        with open(samples_file, "w") as f:
            json.dump({
                "prompts": sample_prompts,
                "generated": generated_samples,
                "timestamp": datetime.now().isoformat()
            }, f, indent=2)

        # Final summary
        total_time = time.time() - overall_start

        console.print(Panel.fit(
            f"✨ [bold green]MAC M2 TRAINING COMPLETE![/bold green] ✨\n\n"
            f"Total Time: {total_time/60:.1f} minutes\n"
            f"Training Loss: {results['train_loss']:.4f}\n"
            f"Model Saved: {PRODUCTION_CONFIG['output_dir']}\n\n"
            f"[bold]Artifacts Created:[/bold]\n"
            f"• Trained model + LoRA adapters\n"
            f"• Training metrics & logs\n"
            f"• Sample generated outputs\n"
            f"• Evaluation results\n\n"
            f"[bold yellow]Next: Generate full narratives with trained model![/bold yellow]",
            border_style="green"
        ))

        return 0

    except Exception as e:
        console.print(f"\n[bold red]❌ Training failed:[/bold red]")
        console.print(f"[red]{str(e)}[/red]")

        import traceback
        traceback.print_exc()

        return 1

    finally:
        if 'trainer' in locals():
            console.print("\n🧹 Cleaning up...")
            trainer.cleanup()

if __name__ == "__main__":
    sys.exit(run_mac_training())