#!/usr/bin/env python3
"""
Document Generation Script

Generate narrative documents using trained models with coherence validation
and multi-format output support.

Usage:
    python generate_documents.py --model ./models/checkpoints --prompt "A tale of..."
    python generate_documents.py --config config/generation_config.yaml --batch-prompts prompts.txt
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional

import yaml
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table

# Import our modules
from finetune.generation import DocumentGenerator, GenerationConfig, DocumentFormat

console = Console()


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """Setup rich logging."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)]
    )
    return logging.getLogger("document_generation")


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate narrative documents using trained models",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single document generation
  python generate_documents.py --model ./models/best --prompt "Chronicle of the Great War"

  # Multiple document types
  python generate_documents.py --model ./models/best --prompt "The Kingdom" --document-types chronicle diary letter

  # Batch generation from file
  python generate_documents.py --model ./models/best --batch-prompts prompts.txt

  # Custom configuration
  python generate_documents.py --config generation_config.yaml

  # Different output formats
  python generate_documents.py --model ./models/best --prompt "Tale" --output-format markdown --export-format html
        """
    )

    # Model and configuration
    parser.add_argument("--model", "-m", required=True, help="Path to trained model")
    parser.add_argument("--config", "-c", type=str, help="Path to generation configuration file")

    # Input options
    parser.add_argument("--prompt", "-p", type=str, help="Generation prompt")
    parser.add_argument("--batch-prompts", type=str, help="File containing multiple prompts")
    parser.add_argument("--document-types", nargs="+",
                       choices=["chronicle", "diary", "letter", "news_article", "legal_document",
                               "song", "map", "inventory", "treaty", "speech"],
                       default=["chronicle"], help="Document types to generate")

    # Generation parameters
    parser.add_argument("--temperature", type=float, default=0.8, help="Generation temperature")
    parser.add_argument("--top-p", type=float, default=0.9, help="Top-p sampling")
    parser.add_argument("--max-tokens", type=int, default=512, help="Maximum new tokens")
    parser.add_argument("--num-sequences", type=int, default=1, help="Number of sequences to generate")

    # Output options
    parser.add_argument("--output-dir", "-o", default="./generated_documents", help="Output directory")
    parser.add_argument("--output-format", choices=["structured", "plain", "json", "markdown", "html"],
                       default="structured", help="Output format")
    parser.add_argument("--export-format", choices=["json", "yaml", "txt", "md", "html"],
                       default="json", help="Export file format")

    # Advanced options
    parser.add_argument("--world-context", type=str, help="JSON file with world context")
    parser.add_argument("--sequence-generation", action="store_true", help="Generate document sequence")
    parser.add_argument("--validate-coherence", action="store_true", default=True, help="Validate coherence")
    parser.add_argument("--coherence-threshold", type=float, default=0.6, help="Coherence threshold")

    # System options
    parser.add_argument("--device", default="auto", help="Device to use (auto, cpu, cuda)")
    parser.add_argument("--load-in-4bit", action="store_true", help="Load model in 4-bit precision")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    parser.add_argument("--seed", type=int, help="Random seed for reproducible generation")

    return parser.parse_args()


def load_generation_config(config_path: Optional[str] = None, args: Optional[argparse.Namespace] = None) -> GenerationConfig:
    """Load generation configuration from file and command line arguments."""

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
            "temperature": args.temperature,
            "top_p": args.top_p,
            "max_new_tokens": args.max_tokens,
            "num_return_sequences": args.num_sequences,
            "validate_coherence": args.validate_coherence,
            "coherence_threshold": args.coherence_threshold,
            "output_format": getattr(DocumentFormat, args.output_format.upper()),
            "seed": args.seed,
        }
        config_dict.update({k: v for k, v in cli_config.items() if v is not None})

    return GenerationConfig(**config_dict)


def load_prompts(args: argparse.Namespace) -> List[str]:
    """Load prompts from command line or file."""

    prompts = []

    if args.prompt:
        prompts.append(args.prompt)

    if args.batch_prompts:
        prompts_file = Path(args.batch_prompts)
        if not prompts_file.exists():
            raise FileNotFoundError(f"Prompts file not found: {prompts_file}")

        with open(prompts_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):  # Skip empty lines and comments
                    prompts.append(line)

    if not prompts:
        raise ValueError("No prompts provided. Use --prompt or --batch-prompts")

    return prompts


def load_world_context(context_path: Optional[str]) -> Optional[Dict]:
    """Load world context from JSON file."""

    if not context_path:
        return None

    context_file = Path(context_path)
    if not context_file.exists():
        raise FileNotFoundError(f"World context file not found: {context_file}")

    with open(context_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def display_generation_info(config: GenerationConfig, prompts: List[str], args: argparse.Namespace):
    """Display generation configuration."""

    # Configuration table
    config_table = Table(title="🎭 Generation Configuration")
    config_table.add_column("Parameter", style="cyan")
    config_table.add_column("Value", style="green")

    config_table.add_row("Model Path", str(args.model))
    config_table.add_row("Document Types", ", ".join(args.document_types))
    config_table.add_row("Temperature", f"{config.temperature}")
    config_table.add_row("Top-p", f"{config.top_p}")
    config_table.add_row("Max Tokens", f"{config.max_new_tokens}")
    config_table.add_row("Coherence Validation", "✅" if config.validate_coherence else "❌")
    config_table.add_row("Output Format", config.output_format.value)

    console.print(config_table)

    # Prompts preview
    prompts_table = Table(title="📝 Generation Prompts")
    prompts_table.add_column("#", style="cyan", width=4)
    prompts_table.add_column("Prompt Preview", style="green")

    for i, prompt in enumerate(prompts[:5], 1):
        preview = prompt[:80] + "..." if len(prompt) > 80 else prompt
        prompts_table.add_row(str(i), preview)

    if len(prompts) > 5:
        prompts_table.add_row("...", f"... and {len(prompts) - 5} more prompts")

    console.print(prompts_table)


def generate_single_document(
    generator: DocumentGenerator,
    prompt: str,
    document_type: str,
    world_context: Optional[Dict] = None,
) -> Dict:
    """Generate a single document."""

    return generator.generate_document(
        prompt=prompt,
        document_type=document_type,
        world_context=world_context,
    )


def generate_document_sequence(
    generator: DocumentGenerator,
    prompt: str,
    document_types: List[str],
    world_context: Optional[Dict] = None,
) -> List[Dict]:
    """Generate a sequence of related documents."""

    return generator.generate_document_sequence(
        initial_prompt=prompt,
        document_types=document_types,
        world_context=world_context,
        maintain_narrative=True,
    )


def export_results(
    results: List[Dict],
    output_dir: Path,
    export_format: str,
    collection_name: str = "generated_documents",
):
    """Export generation results to files."""

    output_dir.mkdir(parents=True, exist_ok=True)

    from finetune.generation.output_formatter import OutputFormatter

    formatter = OutputFormatter()

    # Create document collection
    collection = formatter.format_document_collection(results, include_summary=True)

    # Export collection
    formatter.export_collection(
        collection,
        output_dir,
        format_type=export_format,
        individual_files=True,
    )

    # Create summary file
    summary_file = output_dir / f"generation_summary.{export_format}"

    summary_data = {
        "generation_summary": collection["collection_metadata"],
        "collection_summary": collection.get("summary", {}),
        "total_documents": len(results),
        "document_types": {doc.get("document_type", "unknown"): 1 for doc in results},
    }

    if export_format == "json":
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(summary_data, f, indent=2, ensure_ascii=False)
    elif export_format == "yaml":
        with open(summary_file, "w", encoding="utf-8") as f:
            yaml.dump(summary_data, f, default_flow_style=False, allow_unicode=True)

    console.print(f"📁 Results exported to: {output_dir}")
    console.print(f"📊 Summary saved to: {summary_file}")


def main():
    """Main generation function."""
    args = parse_arguments()

    # Setup logging
    logger = setup_logging(args.log_level)

    console.print("🎭 [bold blue]Narrative Document Generator[/bold blue]")

    try:
        # Load configuration
        config = load_generation_config(args.config, args)

        # Load prompts
        prompts = load_prompts(args)

        # Load world context
        world_context = load_world_context(args.world_context)

        # Display configuration
        display_generation_info(config, prompts, args)

        # Initialize generator
        console.print("🔧 Initializing document generator...")

        generator = DocumentGenerator(
            model_path=args.model,
            config=config,
            device=args.device,
            load_in_4bit=args.load_in_4bit,
        )

        console.print("✅ Generator ready")

        # Generate documents
        results = []

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:

            if args.sequence_generation and len(args.document_types) > 1:
                # Generate document sequences
                task = progress.add_task("Generating document sequences...", total=len(prompts))

                for i, prompt in enumerate(prompts):
                    progress.update(task, description=f"Sequence {i+1}/{len(prompts)}: {prompt[:50]}...")

                    sequence = generate_document_sequence(
                        generator, prompt, args.document_types, world_context
                    )

                    results.extend(sequence)
                    progress.advance(task)

            else:
                # Generate individual documents
                total_docs = len(prompts) * len(args.document_types)
                task = progress.add_task("Generating documents...", total=total_docs)

                for i, prompt in enumerate(prompts):
                    for j, doc_type in enumerate(args.document_types):
                        doc_num = i * len(args.document_types) + j + 1
                        progress.update(task, description=f"Document {doc_num}/{total_docs}: {doc_type}")

                        document = generate_single_document(
                            generator, prompt, doc_type, world_context
                        )

                        results.append(document)
                        progress.advance(task)

        # Display results summary
        console.print(f"🎉 [bold green]Generation Complete![/bold green]")

        results_table = Table(title="📊 Generation Results")
        results_table.add_column("Metric", style="cyan")
        results_table.add_column("Value", style="green")

        total_words = sum(doc.get("metadata", {}).get("word_count", 0) for doc in results)
        avg_coherence = sum(doc.get("metadata", {}).get("coherence_score", 0) for doc in results) / len(results)

        results_table.add_row("Total Documents", str(len(results)))
        results_table.add_row("Total Words", f"{total_words:,}")
        results_table.add_row("Average Coherence", f"{avg_coherence:.3f}")

        console.print(results_table)

        # Export results
        export_results(
            results,
            Path(args.output_dir),
            args.export_format,
        )

        # Show sample outputs
        if results:
            console.print("\n🎭 [bold blue]Sample Generated Content[/bold blue]")

            sample_doc = results[0]
            content = sample_doc.get("content", "")
            doc_type = sample_doc.get("document_type", "unknown")

            console.print(f"[bold cyan]Document Type:[/bold cyan] {doc_type}")
            console.print(f"[bold cyan]Content Preview:[/bold cyan]")

            preview = content[:500] + "..." if len(content) > 500 else content
            console.print(f"[dim]{preview}[/dim]")

        # Cleanup
        generator.cleanup()

        console.print("\n✅ [bold green]All done![/bold green]")

    except KeyboardInterrupt:
        console.print("\n⚠️  [yellow]Generation interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        console.print(f"\n❌ [red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()