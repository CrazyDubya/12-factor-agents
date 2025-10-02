#!/usr/bin/env python3
"""
Lambda.ai A10 Training Script - Budget Option
For 10K document ultra corpus with 5 epochs + early stopping

Hardware: A10 (24GB VRAM)
Estimated time: 4-6 hours (slower than A100 but much cheaper)
Estimated cost: $3-4.50 at $0.75/hr
"""

import json
import sys
import time
from pathlib import Path
from datetime import datetime

import torch
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from finetune.training.model_trainer import ModelTrainer, TrainingConfig

console = Console()

# A10 24GB OPTIMIZED CONFIGURATION (memory-conscious)
A10_CONFIG = {
    "model_name": "qwen-1.5b",
    "training_data_path": "experiments/ultra_corpus_1759240479/training_data.json",
    "output_dir": "./models/ultra_narrative_a10",
    "num_train_epochs": 5,
    "per_device_train_batch_size": 2,  # Smaller for 24GB VRAM
    "gradient_accumulation_steps": 8,  # Effective batch = 16 (same as A100)
    "learning_rate": 5e-5,
    "max_grad_norm": 1.0,
    "warmup_steps": 500,
    "lora_r": 8,  # Lower rank to save memory
    "lora_alpha": 16,
    "use_quantization": True,  # REQUIRED for A10 24GB
    "max_sequence_length": 1024,
    "eval_split": 0.05,
    "eval_steps": 500,
    "save_steps": 1250,
    "early_stopping_patience": 2,
}

console.print(Panel.fit(
    f"☁️ [bold green]Lambda.ai A10 Training (Budget)[/bold green]\n\n"
    f"Hardware: NVIDIA A10 (24GB VRAM)\n"
    f"CUDA acceleration enabled\n\n"
    f"[bold]Configuration:[/bold]\n"
    f"• Model: {A10_CONFIG['model_name']}\n"
    f"• Max Epochs: {A10_CONFIG['num_train_epochs']} (with early stopping)\n"
    f"• Batch Size: {A10_CONFIG['per_device_train_batch_size']} (+ grad acc {A10_CONFIG['gradient_accumulation_steps']})\n"
    f"• Effective Batch: {A10_CONFIG['per_device_train_batch_size'] * A10_CONFIG['gradient_accumulation_steps']}\n"
    f"• 4-bit Quantization: REQUIRED (24GB limit)\n"
    f"• LoRA Rank: {A10_CONFIG['lora_r']} (memory-optimized)\n"
    f"• Expected Time: 4-6 hours\n"
    f"• Expected Cost: $3-4.50 at $0.75/hr",
    border_style="green"
))

def check_device():
    """Check CUDA availability."""
    if not torch.cuda.is_available():
        console.print("❌ [red]CUDA not available. This script requires GPU.[/red]")
        sys.exit(1)

    device = torch.device("cuda")
    gpu_name = torch.cuda.get_device_name(0)
    gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3

    console.print(f"✅ [green]GPU: {gpu_name}[/green]")
    console.print(f"✅ [green]Memory: {gpu_memory:.1f} GB[/green]")

    if gpu_memory < 20:
        console.print("⚠️ [yellow]Warning: Less than 20GB VRAM. Ensure 4-bit quantization is enabled.[/yellow]")

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

    console.print(f"\n✂️ Data split: {len(train_data)} train, {len(eval_data)} eval")

    return train_data, eval_data

def run_a10_training():
    """Execute A10-optimized training."""

    console.print(Panel.fit(
        "🚀 [bold blue]Starting A10 Budget Fine-Tuning[/bold blue]\n" +
        "5 epochs with early stopping (patience=2)\n" +
        "4-bit quantization + LoRA rank 8\n" +
        "A10-optimized for 24GB VRAM (effective batch=16)",
        border_style="blue"
    ))

    overall_start = time.time()
    device = check_device()

    try:
        # Step 1: Load data
        console.print(Panel.fit("📚 [bold]Step 1: Load Training Data[/bold]", border_style="blue"))
        data = load_training_data(A10_CONFIG["training_data_path"])
        train_data, eval_data = split_train_eval(data, A10_CONFIG["eval_split"])

        # Step 2: Initialize trainer
        console.print(Panel.fit("🔧 [bold]Step 2: Initialize ModelTrainer[/bold]", border_style="blue"))

        config = TrainingConfig(
            num_train_epochs=A10_CONFIG["num_train_epochs"],
            per_device_train_batch_size=A10_CONFIG["per_device_train_batch_size"],
            per_device_eval_batch_size=A10_CONFIG["per_device_train_batch_size"],
            gradient_accumulation_steps=A10_CONFIG["gradient_accumulation_steps"],
            learning_rate=A10_CONFIG["learning_rate"],
            warmup_steps=A10_CONFIG["warmup_steps"],
            lora_r=A10_CONFIG["lora_r"],
            lora_alpha=A10_CONFIG["lora_alpha"],
            use_quantization=True,  # REQUIRED for A10
            max_sequence_length=A10_CONFIG["max_sequence_length"],
            fp16=True,  # A10 works best with fp16
            bf16=False,
            gradient_checkpointing=True,
            dataloader_num_workers=2,  # Lower to save memory
            eval_strategy="steps",
            eval_steps=A10_CONFIG["eval_steps"],
            save_steps=A10_CONFIG["save_steps"],
            save_total_limit=A10_CONFIG["num_train_epochs"],
        )

        config.max_grad_norm = A10_CONFIG["max_grad_norm"]

        # Display configuration
        config_table = Table(title="⚙️ A10 Training Configuration")
        config_table.add_column("Parameter", style="cyan")
        config_table.add_column("Value", style="green")

        config_table.add_row("Model", A10_CONFIG["model_name"])
        config_table.add_row("Device", f"{device} (A10 24GB)")
        config_table.add_row("Max Epochs", str(config.num_train_epochs))
        config_table.add_row("Batch Size", str(config.per_device_train_batch_size))
        config_table.add_row("Gradient Accumulation", str(config.gradient_accumulation_steps))
        config_table.add_row("Effective Batch Size", str(config.per_device_train_batch_size * config.gradient_accumulation_steps))
        config_table.add_row("Learning Rate", str(config.learning_rate))
        config_table.add_row("LoRA Rank", str(config.lora_r))
        config_table.add_row("LoRA Alpha", str(config.lora_alpha))
        config_table.add_row("Quantization", "4-bit (QLoRA)")
        config_table.add_row("Precision", "fp16")
        config_table.add_row("Training Documents", str(len(train_data)))
        config_table.add_row("Eval Documents", str(len(eval_data)))

        console.print(config_table)

        trainer = ModelTrainer(
            config=config,
            model_name=A10_CONFIG["model_name"],
            output_dir=A10_CONFIG["output_dir"],
            use_flash_attention=True  # A10 supports Flash Attention 2
        )

        console.print("✅ ModelTrainer initialized")

        # Step 3: Load model
        console.print(Panel.fit("🤖 [bold]Step 3: Load Model & Tokenizer[/bold]", border_style="blue"))
        console.print("Loading Qwen-1.5B (4-bit quantized for A10 24GB)...")

        model, tokenizer = trainer.load_model_and_tokenizer()

        console.print("✅ Model and tokenizer loaded")

        # Step 4: Execute training
        console.print(Panel.fit("🚀 [bold]Step 4: Execute Fine-Tuning[/bold]", border_style="blue"))
        console.print("[bold yellow]Starting A10 training (slower but cheaper)...[/bold yellow]")

        training_start = time.time()

        results = trainer.train(
            train_data=train_data,
            eval_data=eval_data,
            resume_from_checkpoint=None
        )

        training_time = time.time() - training_start

        console.print(f"\n✅ Training complete! Time: {training_time/60:.1f} minutes ({training_time/3600:.1f} hours)")

        # Display results
        results_table = Table(title="📈 Training Results")
        results_table.add_column("Metric", style="cyan")
        results_table.add_column("Value", style="green")

        results_table.add_row("Training Loss", f"{results['train_loss']:.4f}")
        results_table.add_row("Training Runtime", f"{results['train_runtime']/3600:.2f} hours")
        results_table.add_row("Samples/Second", f"{results['train_samples_per_second']:.2f}")
        results_table.add_row("Total Cost", f"${(training_time/3600) * 0.75:.2f} at $0.75/hr")

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
            "<|chronicle|>\nTitle: The Final Discovery\nDate: Year 1260\n\n",
            "<|prophecy|>\nSpoken by: Prophet Iris\nDate: Year 1254\n\nI have seen the end of days, and it is not what we expected...\n\n",
            "<|treaty|>\nBetween: The Crystal Spire and Elderwood\nDate: Year 1250\n\nArticle I: Terms of Alliance\n\n"
        ]

        generated_samples = trainer.generate_sample_outputs(
            prompts=sample_prompts,
            max_new_tokens=300,
            temperature=0.8
        )

        for i, generated in enumerate(generated_samples):
            console.print(f"\n[bold cyan]Sample {i+1}:[/bold cyan]")
            console.print(Panel(generated[:300] + "..." if len(generated) > 300 else generated, border_style="green"))

        # Save samples
        samples_file = Path(A10_CONFIG["output_dir"]) / "sample_outputs.json"
        with open(samples_file, "w") as f:
            json.dump({
                "prompts": sample_prompts,
                "generated": generated_samples,
                "timestamp": datetime.now().isoformat()
            }, f, indent=2)

        # Final summary
        total_time = time.time() - overall_start
        total_cost = (total_time / 3600) * 0.75

        console.print(Panel.fit(
            f"✨ [bold green]A10 TRAINING COMPLETE![/bold green] ✨\n\n"
            f"Total Time: {total_time/60:.1f} minutes ({total_time/3600:.2f} hours)\n"
            f"Total Cost: ${total_cost:.2f} at $0.75/hr\n"
            f"Training Loss: {results['train_loss']:.4f}\n"
            f"Model Saved: {A10_CONFIG['output_dir']}\n\n"
            f"[bold]Artifacts Created:[/bold]\n"
            f"• Trained model + LoRA adapters\n"
            f"• {config.num_train_epochs} checkpoint models\n"
            f"• Training metrics & logs\n"
            f"• Sample generated outputs\n"
            f"• Evaluation results\n\n"
            f"[bold yellow]Next: Download model to local machine![/bold yellow]",
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
    sys.exit(run_a10_training())
