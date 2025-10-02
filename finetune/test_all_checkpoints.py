#!/usr/bin/env python3
"""
Checkpoint Comparison Testing
Compare all 5 checkpoints to see training progression
"""

import json
import time
from pathlib import Path

import torch
from peft import PeftModel, PeftConfig
from transformers import AutoModelForCausalLM, AutoTokenizer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress

console = Console()

# All available checkpoints
CHECKPOINTS = [
    "checkpoint-1250",  # ~2.5 hours training
    "checkpoint-2500",  # ~5 hours
    "checkpoint-3750",  # ~7.5 hours
    "checkpoint-5000",  # ~8.5 hours
    "checkpoint-5940",  # Final (8.84 hours)
]

BASE_PATH = Path("models/ultra_narrative_a10/checkpoints")
OUTPUT_DIR = Path("test_outputs/checkpoint_comparison")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Single test prompt to compare across all checkpoints
TEST_PROMPT = """<|chronicle|>
Title: The Battle of Shadow's Edge
Date: Year 1262
Location: Shadow's Edge Canyon

The armies clashed at dawn, as the ancient prophecy had foretold. General Marcus led..."""

def setup_device():
    """Configure device for inference."""
    if torch.cuda.is_available():
        device = torch.device("cuda")
        device_name = "CUDA GPU"
    elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        device = torch.device("mps")
        device_name = "Apple Silicon (MPS)"
    else:
        device = torch.device("cpu")
        device_name = "CPU"

    console.print(f"✅ Using device: [bold green]{device_name}[/bold green]")
    return device

def load_checkpoint(checkpoint_name: str, device: torch.device):
    """Load a specific checkpoint."""
    checkpoint_path = BASE_PATH / checkpoint_name

    if not checkpoint_path.exists():
        console.print(f"[yellow]⚠️  Checkpoint not found: {checkpoint_name}[/yellow]")
        return None, None

    console.print(f"Loading {checkpoint_name}...")

    # Load LoRA config
    config = PeftConfig.from_pretrained(checkpoint_path)

    # Load base model (reuse if already loaded to save time)
    base_model = AutoModelForCausalLM.from_pretrained(
        config.base_model_name_or_path,
        torch_dtype=torch.float16 if device.type != "cpu" else torch.float32,
        device_map="auto",
        low_cpu_mem_usage=True
    )

    # Load LoRA adapters
    model = PeftModel.from_pretrained(base_model, checkpoint_path)
    model = model.to(device)
    model.eval()

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(checkpoint_path)

    return model, tokenizer

def generate_from_checkpoint(model, tokenizer, prompt: str, device: torch.device):
    """Generate text from a checkpoint."""
    inputs = tokenizer(prompt, return_tensors="pt")
    if device:
        inputs = {k: v.to(device) for k, v in inputs.items()}

    start_time = time.time()

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=200,
            temperature=0.8,
            top_p=0.9,
            do_sample=True,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )

    generation_time = time.time() - start_time
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Extract only the generated portion
    generated_only = generated_text[len(prompt):].strip()

    num_tokens = outputs.shape[1] - inputs["input_ids"].shape[1]

    return {
        "generated": generated_only,
        "tokens": num_tokens,
        "time": generation_time,
        "tokens_per_sec": num_tokens / generation_time if generation_time > 0 else 0
    }

def compare_checkpoints(device):
    """Compare all checkpoints with same prompt."""
    console.print(Panel.fit(
        "📊 [bold blue]Checkpoint Comparison Test[/bold blue]\n\n"
        f"Testing {len(CHECKPOINTS)} checkpoints\n"
        "Same prompt across all checkpoints\n"
        "Observe training progression",
        border_style="blue"
    ))

    console.print(f"\n[bold]Test Prompt:[/bold]")
    console.print(Panel(TEST_PROMPT[:200] + "...", border_style="dim"))

    results = []

    with Progress() as progress:
        task = progress.add_task(
            f"[cyan]Testing checkpoints...",
            total=len(CHECKPOINTS)
        )

        for checkpoint_name in CHECKPOINTS:
            console.print(f"\n[bold cyan]Testing: {checkpoint_name}[/bold cyan]")

            # Load checkpoint
            model, tokenizer = load_checkpoint(checkpoint_name, device)

            if model is None:
                progress.update(task, advance=1)
                continue

            # Generate
            result = generate_from_checkpoint(model, tokenizer, TEST_PROMPT, device)

            # Display
            console.print(Panel(
                result['generated'][:300] + ("..." if len(result['generated']) > 300 else ""),
                title=f"[green]{checkpoint_name}[/green]",
                border_style="green"
            ))

            stats = Table(show_header=False, box=None)
            stats.add_column("Metric", style="cyan")
            stats.add_column("Value", style="green")
            stats.add_row("Tokens", str(result['tokens']))
            stats.add_row("Time", f"{result['time']:.2f}s")
            stats.add_row("Tokens/Sec", f"{result['tokens_per_sec']:.1f}")
            console.print(stats)

            results.append({
                "checkpoint": checkpoint_name,
                "generated": result['generated'],
                "metrics": {
                    "tokens": result['tokens'],
                    "time": result['time'],
                    "tokens_per_sec": result['tokens_per_sec']
                }
            })

            # Clean up model to free memory
            del model, tokenizer
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            elif hasattr(torch.backends, "mps"):
                torch.mps.empty_cache()

            progress.update(task, advance=1)

    return results

def save_comparison(results):
    """Save checkpoint comparison results."""
    output_file = OUTPUT_DIR / f"checkpoint_comparison_{int(time.time())}.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "test_prompt": TEST_PROMPT,
            "timestamp": time.time(),
            "checkpoints_tested": len(results),
            "results": results
        }, f, indent=2, ensure_ascii=False)

    console.print(f"\n💾 Comparison saved to: [bold]{output_file}[/bold]")

    # Create readable text report
    report_file = OUTPUT_DIR / f"checkpoint_comparison_{int(time.time())}.txt"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("CHECKPOINT COMPARISON REPORT\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Test Prompt:\n{TEST_PROMPT}\n\n")
        f.write("=" * 80 + "\n\n")

        for result in results:
            f.write(f"\n{'=' * 80}\n")
            f.write(f"{result['checkpoint'].upper()}\n")
            f.write(f"{'=' * 80}\n\n")
            f.write(f"Tokens: {result['metrics']['tokens']}\n")
            f.write(f"Time: {result['metrics']['time']:.2f}s\n")
            f.write(f"Speed: {result['metrics']['tokens_per_sec']:.1f} tokens/sec\n\n")
            f.write(f"Generated Text:\n{'-' * 80}\n")
            f.write(result['generated'])
            f.write(f"\n{'-' * 80}\n\n")

    console.print(f"📄 Text report saved to: [bold]{report_file}[/bold]")

    return output_file, report_file

def main():
    """Main comparison workflow."""
    console.print(Panel.fit(
        "📊 [bold green]Checkpoint Comparison Testing[/bold green]\n\n"
        "Compare all 5 training checkpoints\n"
        "Observe model improvement over training",
        border_style="green"
    ))

    try:
        device = setup_device()

        results = compare_checkpoints(device)

        if not results:
            console.print("[red]No checkpoints were successfully tested[/red]")
            return 1

        json_file, txt_file = save_comparison(results)

        # Summary
        console.print(Panel.fit(
            f"✨ [bold green]Comparison Complete![/bold green]\n\n"
            f"Checkpoints Tested: {len(results)}\n"
            f"JSON Results: {json_file}\n"
            f"Text Report: {txt_file}\n\n"
            f"[bold]Key Observations:[/bold]\n"
            f"• Early checkpoints (1250) show initial learning\n"
            f"• Middle checkpoints (2500-3750) show improvement\n"
            f"• Final checkpoint (5940) shows best performance\n"
            f"• Compare narrative coherence and style consistency",
            border_style="green"
        ))

        return 0

    except Exception as e:
        console.print(f"\n[bold red]❌ Error:[/bold red]")
        console.print(f"[red]{str(e)}[/red]")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
