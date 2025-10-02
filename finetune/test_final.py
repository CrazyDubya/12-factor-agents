#!/usr/bin/env python3
"""
Final Inference Test - Using Actual Training Data Format
Tests with the exact document types and format from training
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

CHECKPOINT_PATH = Path("models/ultra_narrative_a10/checkpoints/checkpoint-5940")
OUTPUT_DIR = Path("test_outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

def setup_device():
    if torch.cuda.is_available():
        device = torch.device("cuda")
    elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        device = torch.device("mps")
    else:
        device = torch.device("cpu")
    return device

def load_model(checkpoint_path: Path, device: torch.device):
    console.print(f"📂 Loading model...")
    start_time = time.time()

    config = PeftConfig.from_pretrained(checkpoint_path)
    base_model = AutoModelForCausalLM.from_pretrained(
        config.base_model_name_or_path,
        dtype=torch.float16 if device.type != "cpu" else torch.float32,
        device_map="auto",
        low_cpu_mem_usage=True
    )

    model = PeftModel.from_pretrained(base_model, checkpoint_path)
    model = model.to(device)
    model.eval()

    tokenizer = AutoTokenizer.from_pretrained(checkpoint_path)

    console.print(f"✅ Model loaded in {time.time() - start_time:.1f}s\n")
    return model, tokenizer

def generate_narrative(model, tokenizer, prompt: str, device: torch.device, max_tokens: int = 150):
    """Generate with settings optimized for training data format."""
    inputs = tokenizer(prompt, return_tensors="pt")
    if device:
        inputs = {k: v.to(device) for k, v in inputs.items()}

    start_time = time.time()

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            temperature=0.85,
            top_p=0.92,
            top_k=40,
            do_sample=True,
            repetition_penalty=1.15,
            no_repeat_ngram_size=3,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )

    generation_time = time.time() - start_time
    full_text = tokenizer.decode(outputs[0], skip_special_tokens=False)
    generated = full_text[len(prompt):].strip()

    # Clean up output - stop at end tags or text end markers
    end_markers = ['<|end', '<|endoftext|>', '...', '\n\n\n']
    for marker in end_markers:
        if marker in generated:
            idx = generated.find(marker)
            if idx > 50:  # Only cut if we have reasonable content
                generated = generated[:idx].strip()
                break

    num_tokens = len(tokenizer.encode(generated))

    return {
        "generated": generated,
        "tokens": num_tokens,
        "time": generation_time,
        "tokens_per_sec": num_tokens / generation_time if generation_time > 0 else 0
    }

def main():
    console.print(Panel.fit(
        "✨ [bold green]Final Inference Test[/bold green]\n\n"
        "Using actual training data format\n"
        "Document types: chronicle, prophecy, treaty, letter, diary_entry",
        border_style="green"
    ))

    # Test prompts matching training data format
    test_cases = [
        {
            "type": "chronicle",
            "prompt": "<|chronicle|>\nIn the year 1262, great events transpired at Shadow Valley. The forces of Crystal Spire, under Commander Marcus, engaged their ancient adversaries..."
        },
        {
            "type": "prophecy",
            "prompt": "<|prophecy|>\nWhen three moons align in the darkened sky and the ancient stones begin to sing, then shall the Time Keepers return to claim their rightful place. Only those who bear the mark of..."
        },
        {
            "type": "treaty",
            "prompt": "<|treaty|>\nBetween the realm of Elderwood and the dominion of Crystal Spire, this accord is forged. Article I: That all hostilities shall cease upon the signing of this agreement and both parties shall..."
        },
        {
            "type": "letter",
            "prompt": "<|letter|>\nDear Council Members, I write to report a discovery of great significance. During excavations beneath the Old Library, we uncovered artifacts that suggest..."
        },
        {
            "type": "diary_entry",
            "prompt": "<|diary_entry|>\nDay forty-two of the expedition. The ruins grow more magnificent with each passing hour. Today we found inscriptions that match the ancient texts exactly..."
        }
    ]

    try:
        device = setup_device()
        console.print(f"Device: [bold cyan]{device}[/bold cyan]\n")

        model, tokenizer = load_model(CHECKPOINT_PATH, device)

        results = []
        table = Table(title="📊 Generation Results")
        table.add_column("Type", style="cyan")
        table.add_column("Tokens", style="yellow")
        table.add_column("Time", style="green")
        table.add_column("Speed", style="magenta")
        table.add_column("Quality", style="blue")

        for test in test_cases:
            console.print(f"[bold]Generating {test['type']}...[/bold]")

            result = generate_narrative(model, tokenizer, test['prompt'], device, max_tokens=150)

            # Display generated text
            console.print(Panel(
                result['generated'][:400] + ("..." if len(result['generated']) > 400 else ""),
                title=f"[green]{test['type']}[/green]",
                border_style="dim"
            ))

            # Quality assessment (simple heuristics)
            quality = "✅ Good"
            if len(result['generated']) < 50:
                quality = "⚠️ Too short"
            elif '<|' in result['generated'] and result['generated'].count('<|') > 2:
                quality = "⚠️ Format issues"

            table.add_row(
                test['type'],
                str(result['tokens']),
                f"{result['time']:.1f}s",
                f"{result['tokens_per_sec']:.1f}/s",
                quality
            )

            results.append({
                "type": test['type'],
                "prompt": test['prompt'],
                "generated": result['generated'],
                "metrics": {
                    "tokens": result['tokens'],
                    "time": result['time'],
                    "tokens_per_sec": result['tokens_per_sec']
                }
            })

        console.print("\n")
        console.print(table)

        # Save results
        output_file = OUTPUT_DIR / f"final_test_{int(time.time())}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump({
                "checkpoint": "checkpoint-5940",
                "timestamp": time.time(),
                "device": str(device),
                "results": results
            }, f, indent=2, ensure_ascii=False)

        # Summary
        avg_speed = sum(r['metrics']['tokens_per_sec'] for r in results) / len(results)
        total_tokens = sum(r['metrics']['tokens'] for r in results)

        console.print(Panel.fit(
            f"✨ [bold green]Testing Complete![/bold green]\n\n"
            f"Tests: {len(results)}\n"
            f"Total tokens: {total_tokens}\n"
            f"Avg speed: {avg_speed:.1f} tokens/sec\n"
            f"Device: {device}\n\n"
            f"Results saved: {output_file.name}",
            border_style="green"
        ))

        return 0

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
