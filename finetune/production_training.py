#!/usr/bin/env python3
"""
Production Training Pipeline - Real Fine-Tuning with QLoRA

This script performs ACTUAL model training (not simulation) using:
- Best training data: 2000 documents, 7 types
- QLoRA with 4-bit quantization
- 5 epochs for optimal convergence
- Comprehensive evaluation and sample generation
"""

import json
import sys
import time
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table

# Import actual training modules
from finetune.training.model_trainer import ModelTrainer, TrainingConfig
from finetune.config import SUPPORTED_MODELS

console = Console()

# Production configuration based on extensive experiment results
PRODUCTION_CONFIG = {
    "model_name": "qwen-1.5b",
    "training_data_path": "experiments/extensive_1759206645/training_data.json",
    "output_dir": "./models/production_narrative_model",
    "num_train_epochs": 5,
    "per_device_train_batch_size": 4,
    "gradient_accumulation_steps": 4,  # Effective batch size = 16
    "learning_rate": 2e-4,
    "lora_r": 16,
    "lora_alpha": 32,
    "use_quantization": True,
    "max_sequence_length": 2048,
    "eval_split": 0.1,  # 10% for evaluation
}

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

    # Type distribution
    type_table = Table(title="📋 Document Type Distribution")
    type_table.add_column("Type", style="cyan")
    type_table.add_column("Count", style="green")
    type_table.add_column("Percentage", style="yellow")

    for dtype, count in sorted(doc_types.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(data)) * 100
        type_table.add_row(dtype, str(count), f"{percentage:.1f}%")

    console.print(type_table)

    return data

def split_train_eval(data, eval_ratio=0.1):
    """Split data into train and eval sets."""
    import random
    random.seed(42)  # Reproducible split

    shuffled = data.copy()
    random.shuffle(shuffled)

    split_idx = int(len(shuffled) * (1 - eval_ratio))
    train_data = shuffled[:split_idx]
    eval_data = shuffled[split_idx:]

    console.print(f"\n✂️ Data split: {len(train_data)} train, {len(eval_data)} eval")

    return train_data, eval_data

def create_production_trainer():
    """Initialize ModelTrainer with production configuration."""
    console.print("\n🔧 Initializing Production ModelTrainer...")

    # Create training configuration (using ModelTrainer's extended TrainingConfig)
    from finetune.training.model_trainer import TrainingConfig as ExtendedTrainingConfig

    config = ExtendedTrainingConfig(
        num_train_epochs=PRODUCTION_CONFIG["num_train_epochs"],
        per_device_train_batch_size=PRODUCTION_CONFIG["per_device_train_batch_size"],
        per_device_eval_batch_size=PRODUCTION_CONFIG["per_device_train_batch_size"],
        gradient_accumulation_steps=PRODUCTION_CONFIG["gradient_accumulation_steps"],
        learning_rate=PRODUCTION_CONFIG["learning_rate"],
        lora_r=PRODUCTION_CONFIG["lora_r"],
        lora_alpha=PRODUCTION_CONFIG["lora_alpha"],
        use_quantization=PRODUCTION_CONFIG["use_quantization"],
        max_sequence_length=PRODUCTION_CONFIG["max_sequence_length"],
    )

    # Display configuration
    config_table = Table(title="⚙️ Training Configuration")
    config_table.add_column("Parameter", style="cyan")
    config_table.add_column("Value", style="green")

    config_table.add_row("Model", PRODUCTION_CONFIG["model_name"])
    config_table.add_row("Epochs", str(config.num_train_epochs))
    config_table.add_row("Batch Size", str(config.per_device_train_batch_size))
    config_table.add_row("Gradient Accumulation", str(config.gradient_accumulation_steps))
    config_table.add_row("Effective Batch Size", str(config.per_device_train_batch_size * config.gradient_accumulation_steps))
    config_table.add_row("Learning Rate", str(config.learning_rate))
    config_table.add_row("LoRA Rank", str(config.lora_r))
    config_table.add_row("LoRA Alpha", str(config.lora_alpha))
    config_table.add_row("Quantization", "4-bit NF4" if config.use_quantization else "None")
    config_table.add_row("Max Sequence Length", str(config.max_sequence_length))

    console.print(config_table)

    # Initialize trainer
    trainer = ModelTrainer(
        config=config,
        model_name=PRODUCTION_CONFIG["model_name"],
        output_dir=PRODUCTION_CONFIG["output_dir"],
        use_flash_attention=False  # Set to True if supported
    )

    console.print("✅ ModelTrainer initialized")

    return trainer, config

def run_production_training():
    """Execute the complete production training pipeline."""

    console.print(Panel.fit(
        "🚀 [bold green]Production Training Pipeline[/bold green]\n" +
        "Real Fine-Tuning with QLoRA\n" +
        f"Using best configuration: 2000 docs, 5 epochs",
        border_style="green"
    ))

    overall_start = time.time()

    try:
        # Step 1: Load training data
        console.print(Panel.fit("📚 [bold blue]Step 1: Load Training Data[/bold blue]", border_style="blue"))
        data = load_training_data(PRODUCTION_CONFIG["training_data_path"])

        # Step 2: Split data
        train_data, eval_data = split_train_eval(data, PRODUCTION_CONFIG["eval_split"])

        # Step 3: Initialize trainer
        console.print(Panel.fit("🔧 [bold blue]Step 2: Initialize ModelTrainer[/bold blue]", border_style="blue"))
        trainer, config = create_production_trainer()

        # Step 4: Load model and tokenizer
        console.print(Panel.fit("🤖 [bold blue]Step 3: Load Model & Tokenizer[/bold blue]", border_style="blue"))
        console.print("Loading Qwen-1.5B with 4-bit quantization...")

        model, tokenizer = trainer.load_model_and_tokenizer()

        console.print("✅ Model and tokenizer loaded")
        console.print(f"📊 Model: {SUPPORTED_MODELS[PRODUCTION_CONFIG['model_name']].name}")
        console.print(f"💾 Size: {SUPPORTED_MODELS[PRODUCTION_CONFIG['model_name']].size}")

        # Step 5: Execute training
        console.print(Panel.fit("🚀 [bold blue]Step 4: Execute Fine-Tuning[/bold blue]", border_style="blue"))
        console.print("[bold yellow]Starting actual model training...[/bold yellow]")
        console.print(f"Expected time: ~30-60 minutes on consumer GPU")
        console.print(f"Training samples: {len(train_data)}")
        console.print(f"Validation samples: {len(eval_data)}")

        training_start = time.time()

        # ACTUAL TRAINING - This modifies model weights!
        results = trainer.train(
            train_data=train_data,
            eval_data=eval_data,
            resume_from_checkpoint=None
        )

        training_time = time.time() - training_start

        console.print(f"\n✅ Training complete! Time: {training_time/60:.1f} minutes")

        # Display training results
        results_table = Table(title="📈 Training Results")
        results_table.add_column("Metric", style="cyan")
        results_table.add_column("Value", style="green")

        results_table.add_row("Training Loss", f"{results['train_loss']:.4f}")
        results_table.add_row("Training Runtime", f"{results['train_runtime']:.1f}s")
        results_table.add_row("Samples/Second", f"{results['train_samples_per_second']:.2f}")
        results_table.add_row("Total Time", f"{training_time/60:.1f} min")

        console.print(results_table)

        # Step 6: Evaluation
        console.print(Panel.fit("📊 [bold blue]Step 5: Model Evaluation[/bold blue]", border_style="blue"))
        console.print("Running comprehensive evaluation...")

        eval_results = trainer.evaluate_model(eval_data, save_results=True)

        # Display evaluation results
        eval_table = Table(title="📊 Evaluation Metrics")
        eval_table.add_column("Metric", style="cyan")
        eval_table.add_column("Value", style="green")

        if "eval_loss" in eval_results:
            eval_table.add_row("Evaluation Loss", f"{eval_results['eval_loss']:.4f}")
        if "eval_coherence_score" in eval_results:
            eval_table.add_row("Coherence Score", f"{eval_results.get('eval_coherence_score', 0):.3f}")
        if "eval_perplexity" in eval_results:
            eval_table.add_row("Perplexity", f"{eval_results.get('eval_perplexity', 0):.2f}")

        console.print(eval_table)

        # Step 7: Generate samples
        console.print(Panel.fit("📝 [bold blue]Step 6: Generate Sample Narratives[/bold blue]", border_style="blue"))
        console.print("Generating sample documents with fine-tuned model...")

        sample_prompts = [
            "<|chronicle|>\nTitle: The Discovery at Dawn\nDate: Year 1245, Third Moon\nLocation: The Wastes\n\nCURRENT EVENTS:\n",
            "<|diary_entry|>\nAuthor: Chronicler Aria\nDate: Personal Record, Day 500\n\nDear Journal,\n\nToday marks a turning point in",
            "<|letter|>\nFrom: Ambassador Kael\nTo: Archmage Lysander\nDate: Official Correspondence #5000\n\nEsteemed Archmage,\n\nI write regarding the urgent matter of"
        ]

        generated_samples = trainer.generate_sample_outputs(
            prompts=sample_prompts,
            max_new_tokens=256,
            temperature=0.8,
            top_p=0.9
        )

        # Display samples
        for i, (prompt, generated) in enumerate(zip(sample_prompts, generated_samples)):
            console.print(f"\n[bold cyan]Sample {i+1}:[/bold cyan]")
            console.print(Panel(generated[:300] + "...", title=f"Generated Output", border_style="green"))

        # Save samples
        samples_file = Path(PRODUCTION_CONFIG["output_dir"]) / "sample_outputs.json"
        with open(samples_file, "w") as f:
            json.dump({
                "prompts": sample_prompts,
                "generated": generated_samples,
                "timestamp": datetime.now().isoformat()
            }, f, indent=2)

        console.print(f"\n💾 Samples saved to: {samples_file}")

        # Final summary
        total_time = time.time() - overall_start

        console.print(Panel.fit(
            f"✨ [bold green]PRODUCTION TRAINING COMPLETE![/bold green] ✨\n\n"
            f"Total Time: {total_time/60:.1f} minutes\n"
            f"Training Loss: {results['train_loss']:.4f}\n"
            f"Model Saved: {PRODUCTION_CONFIG['output_dir']}\n\n"
            f"[bold yellow]Next Steps:[/bold yellow]\n"
            f"1. Review sample outputs above\n"
            f"2. Generate full narratives with trained model\n"
            f"3. Compare base vs fine-tuned quality\n"
            f"4. Deploy for production use",
            border_style="green"
        ))

        # Save final summary
        summary = {
            "config": PRODUCTION_CONFIG,
            "training_results": results,
            "evaluation_results": eval_results,
            "total_time_minutes": total_time / 60,
            "timestamp": datetime.now().isoformat()
        }

        summary_file = Path(PRODUCTION_CONFIG["output_dir"]) / "training_summary.json"
        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2)

        console.print(f"\n📊 Full summary saved: {summary_file}")

        return 0

    except Exception as e:
        console.print(f"\n[bold red]❌ Training failed with error:[/bold red]")
        console.print(f"[red]{str(e)}[/red]")

        import traceback
        console.print("\n[bold]Traceback:[/bold]")
        traceback.print_exc()

        return 1

    finally:
        # Cleanup
        if 'trainer' in locals():
            console.print("\n🧹 Cleaning up resources...")
            trainer.cleanup()

if __name__ == "__main__":
    sys.exit(run_production_training())