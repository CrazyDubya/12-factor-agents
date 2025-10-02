#!/usr/bin/env python3
"""
Narrative Model Training Script

Complete training pipeline for fine-tuning language models on synthetic
narrative data for coherent document generation and world-building.

Usage:
    python train_narrative_model.py --config config/training_config.yaml
    python train_narrative_model.py --model qwen-1.5b --epochs 3 --batch-size 4
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import torch
import yaml
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

# Import our modules
from finetune.config import SUPPORTED_MODELS, TrainingConfig
from finetune.training import ModelTrainer, EvaluationManager, DatasetManager
from finetune.training.training_utils import TrainingLogger, ModelSaver, TrainingUtils
from finetune.data_generation import SyntheticDataGenerator
from finetune.agents import AgentCoordinator

console = Console()


def setup_logging(log_level: str = "INFO", log_dir: str = "./logs") -> logging.Logger:
    """Setup rich logging."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)]
    )
    return logging.getLogger("narrative_training")


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Train narrative generation models with synthetic data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic training
  python train_narrative_model.py --model qwen-1.5b

  # Custom configuration
  python train_narrative_model.py --config my_config.yaml

  # Quick training with specific parameters
  python train_narrative_model.py --model llama-3b --epochs 2 --batch-size 2 --max-samples 1000

  # Generate data and train
  python train_narrative_model.py --generate-data --num-documents 500 --model qwen-1.5b
        """
    )

    # Model and data
    parser.add_argument("--model", "-m", default="qwen-1.5b", choices=list(SUPPORTED_MODELS.keys()),
                       help="Model to train")
    parser.add_argument("--config", "-c", type=str, help="Path to configuration file")
    parser.add_argument("--data-path", type=str, help="Path to training data")
    parser.add_argument("--output-dir", "-o", default="./models", help="Output directory")

    # Training parameters
    parser.add_argument("--epochs", type=int, default=3, help="Number of training epochs")
    parser.add_argument("--batch-size", type=int, default=4, help="Training batch size")
    parser.add_argument("--learning-rate", type=float, default=2e-4, help="Learning rate")
    parser.add_argument("--max-length", type=int, default=2048, help="Maximum sequence length")

    # Data generation
    parser.add_argument("--generate-data", action="store_true", help="Generate synthetic data")
    parser.add_argument("--num-documents", type=int, default=1000, help="Number of documents to generate")
    parser.add_argument("--num-worlds", type=int, default=5, help="Number of worlds to create")
    parser.add_argument("--max-samples", type=int, help="Maximum training samples to use")

    # Advanced options
    parser.add_argument("--use-quantization", action="store_true", help="Use 4-bit quantization")
    parser.add_argument("--use-flash-attention", action="store_true", help="Use Flash Attention 2")
    parser.add_argument("--resume-from", type=str, help="Resume training from checkpoint")
    parser.add_argument("--eval-only", action="store_true", help="Only run evaluation")

    # Logging and monitoring
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    parser.add_argument("--use-wandb", action="store_true", help="Use Weights & Biases logging")
    parser.add_argument("--experiment-name", type=str, help="Experiment name")

    return parser.parse_args()


def load_config(config_path: Optional[str] = None, args: Optional[argparse.Namespace] = None) -> TrainingConfig:
    """Load configuration from file and command line arguments."""

    config_dict = {}

    # Load from file if provided
    if config_path and Path(config_path).exists():
        with open(config_path, 'r') as f:
            if config_path.endswith('.yaml') or config_path.endswith('.yml'):
                config_dict = yaml.safe_load(f)
            else:
                config_dict = json.load(f)

    # Override with command line arguments
    if args:
        cli_config = {
            "num_train_epochs": args.epochs,
            "per_device_train_batch_size": args.batch_size,
            "learning_rate": args.learning_rate,
            "max_sequence_length": args.max_length,
            "use_quantization": args.use_quantization,
        }
        config_dict.update({k: v for k, v in cli_config.items() if v is not None})

    return TrainingConfig(**config_dict)


def generate_synthetic_data(args: argparse.Namespace, logger: logging.Logger) -> List[Dict]:
    """Generate synthetic training data using the agent system."""

    logger.info("🎭 Starting synthetic data generation...")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:

        # Initialize data generator
        task = progress.add_task("Initializing data generator...", total=None)

        data_generator = SyntheticDataGenerator()

        progress.update(task, description="Generating worlds and documents...")

        # Generate data
        generated_data = []

        for world_idx in range(args.num_worlds):
            progress.update(task, description=f"Creating world {world_idx + 1}/{args.num_worlds}...")

            # Create world
            world_data = data_generator.create_world(
                world_name=f"World_{world_idx + 1}",
                num_characters=8,
                num_locations=6,
            )

            # Generate documents for this world
            world_documents = data_generator.generate_world_documents(
                world_data,
                num_documents=args.num_documents // args.num_worlds,
                document_types=["chronicle", "diary", "letter", "news_article", "song"],
            )

            generated_data.extend(world_documents)

        progress.update(task, description=f"Generated {len(generated_data)} documents", completed=True)

    logger.info(f"✅ Generated {len(generated_data)} synthetic documents across {args.num_worlds} worlds")
    return generated_data


def load_training_data(args: argparse.Namespace, logger: logging.Logger) -> Tuple[List[Dict], Optional[List[Dict]]]:
    """Load or generate training data."""

    if args.generate_data:
        # Generate synthetic data
        train_data = generate_synthetic_data(args, logger)

        # Split into train/eval (80/20)
        split_idx = int(len(train_data) * 0.8)
        eval_data = train_data[split_idx:]
        train_data = train_data[:split_idx]

        logger.info(f"📊 Split data: {len(train_data)} train, {len(eval_data)} eval")

    elif args.data_path:
        # Load from file
        logger.info(f"📂 Loading data from: {args.data_path}")

        data_path = Path(args.data_path)
        if not data_path.exists():
            raise FileNotFoundError(f"Data file not found: {data_path}")

        # Load based on extension
        if data_path.suffix == ".json":
            with open(data_path, 'r') as f:
                data = json.load(f)
        elif data_path.suffix == ".jsonl":
            data = []
            with open(data_path, 'r') as f:
                for line in f:
                    data.append(json.loads(line.strip()))
        else:
            raise ValueError(f"Unsupported data format: {data_path.suffix}")

        # Split data
        split_idx = int(len(data) * 0.8)
        train_data = data[:split_idx]
        eval_data = data[split_idx:] if split_idx < len(data) else None

    else:
        raise ValueError("Either --generate-data or --data-path must be specified")

    # Limit samples if requested
    if args.max_samples:
        train_data = train_data[:args.max_samples]
        if eval_data:
            eval_data = eval_data[:max(100, args.max_samples // 10)]
        logger.info(f"🔢 Limited to {len(train_data)} training samples")

    return train_data, eval_data


def display_training_info(config: TrainingConfig, train_data: List[Dict], args: argparse.Namespace):
    """Display training configuration and data information."""

    # Model info table
    model_table = Table(title="🤖 Model Configuration")
    model_table.add_column("Parameter", style="cyan")
    model_table.add_column("Value", style="green")

    model_info = SUPPORTED_MODELS[args.model]
    model_table.add_row("Model", f"{model_info.name} ({model_info.size})")
    model_table.add_row("Model ID", model_info.model_id)
    model_table.add_row("Max Length", str(config.max_sequence_length))
    model_table.add_row("Quantization", "✅ 4-bit" if config.use_quantization else "❌")
    model_table.add_row("LoRA Rank", str(config.lora_r))

    console.print(model_table)

    # Training config table
    train_table = Table(title="🚀 Training Configuration")
    train_table.add_column("Parameter", style="cyan")
    train_table.add_column("Value", style="green")

    train_table.add_row("Epochs", str(config.num_train_epochs))
    train_table.add_row("Batch Size", str(config.per_device_train_batch_size))
    train_table.add_row("Learning Rate", f"{config.learning_rate:.2e}")
    train_table.add_row("Warmup Steps", str(config.warmup_steps))
    train_table.add_row("Weight Decay", str(config.weight_decay))

    console.print(train_table)

    # Data info
    data_table = Table(title="📚 Dataset Information")
    data_table.add_column("Metric", style="cyan")
    data_table.add_column("Value", style="green")

    data_table.add_row("Training Samples", str(len(train_data)))

    # Document type distribution
    doc_types = {}
    for item in train_data[:1000]:  # Sample first 1000
        doc_type = item.get("document_type", "unknown")
        doc_types[doc_type] = doc_types.get(doc_type, 0) + 1

    top_types = sorted(doc_types.items(), key=lambda x: x[1], reverse=True)[:5]
    data_table.add_row("Top Doc Types", ", ".join([f"{t}: {c}" for t, c in top_types]))

    console.print(data_table)


def main():
    """Main training function."""
    args = parse_arguments()

    # Setup logging
    logger = setup_logging(args.log_level)

    console.print("🎭 [bold blue]Narrative Model Training Pipeline[/bold blue]")
    console.print(f"📦 Model: {args.model}")

    try:
        # Load configuration
        config = load_config(args.config, args)

        # Load training data
        train_data, eval_data = load_training_data(args, logger)

        # Display configuration
        display_training_info(config, train_data, args)

        # Initialize trainer
        logger.info("🔧 Initializing model trainer...")

        trainer = ModelTrainer(
            config=config,
            model_name=args.model,
            output_dir=args.output_dir,
            use_flash_attention=args.use_flash_attention,
        )

        # Load model and tokenizer
        logger.info("📥 Loading model and tokenizer...")
        trainer.load_model_and_tokenizer()

        # Display model info
        model_size_info = TrainingUtils.calculate_model_size(trainer.model)
        memory_info = TrainingUtils.estimate_memory_usage(
            trainer.model,
            config.per_device_train_batch_size,
            config.max_sequence_length,
        )

        console.print(f"📊 Model: {model_size_info['trainable_parameters']:,} trainable parameters")
        console.print(f"🧠 Estimated GPU memory: {memory_info['total_gb']:.1f} GB")

        if args.eval_only:
            # Evaluation only
            logger.info("📈 Running evaluation only...")

            if not eval_data:
                logger.error("No evaluation data available")
                sys.exit(1)

            results = trainer.evaluate_model(eval_data)

            console.print("📊 [bold green]Evaluation Results[/bold green]")
            eval_table = Table()
            eval_table.add_column("Metric", style="cyan")
            eval_table.add_column("Score", style="green")

            key_metrics = [
                ("Overall Score", "overall_score"),
                ("Coherence", "overall_coherence"),
                ("Quality", "overall_quality"),
                ("Perplexity", "perplexity"),
            ]

            for name, key in key_metrics:
                value = results.get(key, 0.0)
                eval_table.add_row(name, f"{value:.3f}")

            console.print(eval_table)

        else:
            # Full training
            logger.info("🚀 Starting training...")

            with console.status("[bold green]Training model...") as status:
                results = trainer.train(
                    train_data=train_data,
                    eval_data=eval_data,
                    resume_from_checkpoint=args.resume_from,
                )

            # Display results
            console.print("🎉 [bold green]Training Complete![/bold green]")

            results_table = Table(title="📊 Training Results")
            results_table.add_column("Metric", style="cyan")
            results_table.add_column("Value", style="green")

            results_table.add_row("Final Loss", f"{results['train_loss']:.4f}")
            results_table.add_row("Training Time", f"{results['train_runtime']:.1f}s")
            results_table.add_row("Samples/Second", f"{results['train_samples_per_second']:.1f}")
            results_table.add_row("Model Path", str(Path(args.output_dir) / "checkpoints"))

            console.print(results_table)

            # Generate sample outputs
            logger.info("🎨 Generating sample outputs...")

            sample_prompts = [
                "<|chronicle|>\nTitle: The Great War Begins\nDate: 1347\n\nIn the third year of King",
                "<|diary_entry|>\nAuthor: Elena Brightwater\nDate: Summer 1348\n\nToday I witnessed something",
                "<|letter|>\nFrom: Captain Marcus\nTo: Lady Catherine\nDate: Autumn 1348\n\nMy beloved,",
            ]

            generated_samples = trainer.generate_sample_outputs(
                sample_prompts, max_new_tokens=200, temperature=0.8
            )

            console.print("\n🎭 [bold blue]Sample Generated Outputs[/bold blue]")
            for i, (prompt, generated) in enumerate(zip(sample_prompts, generated_samples)):
                console.print(f"\n[bold cyan]Sample {i+1}:[/bold cyan]")
                console.print(f"[dim]{prompt}[/dim]{generated}")

        # Cleanup
        trainer.cleanup()

        console.print("\n✅ [bold green]All done![/bold green]")

    except KeyboardInterrupt:
        console.print("\n⚠️  [yellow]Training interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Training failed: {e}")
        console.print(f"\n❌ [red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()