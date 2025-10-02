#!/usr/bin/env python3
"""
Local Inference Testing for A10 Fine-Tuned Model
Tests the trained narrative generation model on Apple Silicon (MPS) or CPU
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

console = Console()

# Model paths
CHECKPOINT_PATH = Path("models/ultra_narrative_a10/checkpoints/checkpoint-5940")
OUTPUT_DIR = Path("test_outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

def setup_device():
    """Configure device for inference (MPS/CUDA/CPU)."""
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

def load_model(checkpoint_path: Path, device: torch.device):
    """Load the fine-tuned model with LoRA adapters."""
    console.print(f"\n📂 Loading model from: {checkpoint_path}")

    start_time = time.time()

    # Load LoRA configuration
    console.print("Loading LoRA configuration...")
    config = PeftConfig.from_pretrained(checkpoint_path)

    # Load base model
    console.print(f"Loading base model: {config.base_model_name_or_path}")
    base_model = AutoModelForCausalLM.from_pretrained(
        config.base_model_name_or_path,
        torch_dtype=torch.float16 if device.type != "cpu" else torch.float32,
        device_map="auto",
        low_cpu_mem_usage=True
    )

    # Load LoRA adapters
    console.print("Loading LoRA adapters...")
    model = PeftModel.from_pretrained(base_model, checkpoint_path)
    model = model.to(device)
    model.eval()

    # Load tokenizer
    console.print("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(checkpoint_path)

    load_time = time.time() - start_time
    console.print(f"✅ Model loaded in {load_time:.2f} seconds\n")

    return model, tokenizer

def generate_text(
    model,
    tokenizer,
    prompt: str,
    max_new_tokens: int = 300,
    temperature: float = 0.8,
    top_p: float = 0.9,
    device: torch.device = None
):
    """Generate text from a prompt."""
    # Tokenize input
    inputs = tokenizer(prompt, return_tensors="pt")
    if device:
        inputs = {k: v.to(device) for k, v in inputs.items()}

    # Generate
    start_time = time.time()

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
            do_sample=True,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )

    generation_time = time.time() - start_time

    # Decode output
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=False)

    # Calculate tokens per second
    num_tokens = outputs.shape[1] - inputs["input_ids"].shape[1]
    tokens_per_sec = num_tokens / generation_time if generation_time > 0 else 0

    return {
        "full_text": generated_text,
        "generated_only": generated_text[len(prompt):],
        "num_tokens": num_tokens,
        "generation_time": generation_time,
        "tokens_per_sec": tokens_per_sec
    }

def run_test_suite(model, tokenizer, device):
    """Run comprehensive test suite."""
    console.print(Panel.fit(
        "🧪 [bold blue]Running Inference Test Suite[/bold blue]\n"
        "Testing 3 narrative types with trained model",
        border_style="blue"
    ))

    # Test prompts matching training data format
    test_cases = [
        {
            "name": "Chronicle",
            "prompt": "<|chronicle|>\nTitle: The Discovery of the Ancient Ruins\nDate: Year 1265\nLocation: The Obsidian Wastes\n\n"
        },
        {
            "name": "Prophecy",
            "prompt": "<|prophecy|>\nSpoken by: Prophet Seer Elara\nDate: Year 1268\nLocation: The Crystal Temple\n\nA great darkness approaches from beyond the mountains, and only those who...\n\n"
        },
        {
            "name": "Treaty",
            "prompt": "<|treaty|>\nBetween: The Kingdom of Luminara and The Shadow Collective\nDate: Year 1270\n\nArticle I: Cessation of Hostilities\n\n"
        }
    ]

    results = []

    for i, test in enumerate(test_cases, 1):
        console.print(f"\n[bold cyan]Test {i}/{len(test_cases)}: {test['name']}[/bold cyan]")
        console.print(f"[dim]Prompt: {test['prompt'][:80]}...[/dim]\n")

        # Generate
        result = generate_text(
            model,
            tokenizer,
            test['prompt'],
            max_new_tokens=300,
            temperature=0.8,
            device=device
        )

        # Display results
        console.print(Panel(
            result['generated_only'][:500] + ("..." if len(result['generated_only']) > 500 else ""),
            title=f"[bold green]Generated {test['name']}[/bold green]",
            border_style="green"
        ))

        # Stats table
        stats = Table(show_header=False, box=None)
        stats.add_column("Metric", style="cyan")
        stats.add_column("Value", style="green")
        stats.add_row("Tokens Generated", str(result['num_tokens']))
        stats.add_row("Generation Time", f"{result['generation_time']:.2f}s")
        stats.add_row("Tokens/Second", f"{result['tokens_per_sec']:.1f}")
        console.print(stats)

        # Save result
        results.append({
            "test_name": test['name'],
            "prompt": test['prompt'],
            "generated": result['generated_only'],
            "metrics": {
                "tokens": result['num_tokens'],
                "time": result['generation_time'],
                "tokens_per_sec": result['tokens_per_sec']
            }
        })

    return results

def save_results(results, checkpoint_name: str):
    """Save test results to JSON."""
    output_file = OUTPUT_DIR / f"inference_test_{checkpoint_name}_{int(time.time())}.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "checkpoint": checkpoint_name,
            "timestamp": time.time(),
            "results": results
        }, f, indent=2, ensure_ascii=False)

    console.print(f"\n💾 Results saved to: [bold]{output_file}[/bold]")
    return output_file

def main():
    """Main testing workflow."""
    console.print(Panel.fit(
        "🧪 [bold green]Local Inference Testing[/bold green]\n\n"
        "Testing A10 fine-tuned narrative model\n"
        "Checkpoint: checkpoint-5940 (final)\n"
        "Model: Qwen-1.5B + LoRA adapters",
        border_style="green"
    ))

    try:
        # Setup
        device = setup_device()

        # Load model
        model, tokenizer = load_model(CHECKPOINT_PATH, device)

        # Run tests
        results = run_test_suite(model, tokenizer, device)

        # Save results
        output_file = save_results(results, "checkpoint-5940")

        # Final summary
        console.print(Panel.fit(
            f"✨ [bold green]Testing Complete![/bold green]\n\n"
            f"Tests Run: {len(results)}\n"
            f"Results Saved: {output_file}\n\n"
            f"[bold]Next Steps:[/bold]\n"
            f"• Review generated narratives in {output_file}\n"
            f"• Run batch_test_narratives.py for comprehensive testing\n"
            f"• Run test_all_checkpoints.py to compare training progression",
            border_style="green"
        ))

    except Exception as e:
        console.print(f"\n[bold red]❌ Error during testing:[/bold red]")
        console.print(f"[red]{str(e)}[/red]")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
