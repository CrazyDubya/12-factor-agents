#!/usr/bin/env python3
"""
Improved Local Inference Testing
With better generation settings to avoid repetition
"""

import json
import time
from pathlib import Path

import torch
from peft import PeftModel, PeftConfig
from transformers import AutoModelForCausalLM, AutoTokenizer
from rich.console import Console
from rich.panel import Panel

console = Console()

CHECKPOINT_PATH = Path("models/ultra_narrative_a10/checkpoints/checkpoint-5940")
OUTPUT_DIR = Path("test_outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

def setup_device():
    """Configure device."""
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
    """Load the fine-tuned model."""
    console.print(f"\n📂 Loading model from: {checkpoint_path}")

    start_time = time.time()

    config = PeftConfig.from_pretrained(checkpoint_path)

    console.print(f"Loading base model: {config.base_model_name_or_path}")
    base_model = AutoModelForCausalLM.from_pretrained(
        config.base_model_name_or_path,
        dtype=torch.float16 if device.type != "cpu" else torch.float32,
        device_map="auto",
        low_cpu_mem_usage=True
    )

    console.print("Loading LoRA adapters...")
    model = PeftModel.from_pretrained(base_model, checkpoint_path)
    model = model.to(device)
    model.eval()

    console.print("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(checkpoint_path)

    load_time = time.time() - start_time
    console.print(f"✅ Model loaded in {load_time:.2f} seconds\n")

    return model, tokenizer

def generate_text_improved(
    model,
    tokenizer,
    prompt: str,
    max_new_tokens: int = 200,
    device: torch.device = None
):
    """Generate text with improved settings to avoid repetition."""
    inputs = tokenizer(prompt, return_tensors="pt")
    if device:
        inputs = {k: v.to(device) for k, v in inputs.items()}

    start_time = time.time()

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=0.9,           # Higher for more variety
            top_p=0.95,                # Nucleus sampling
            top_k=50,                  # Limit vocabulary
            do_sample=True,
            repetition_penalty=1.2,    # Penalize repetition
            no_repeat_ngram_size=3,    # Prevent 3-gram repetition
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )

    generation_time = time.time() - start_time
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=False)

    # Extract only the new text
    generated_only = generated_text[len(prompt):].strip()

    # Stop at end tags to avoid repetition
    end_tags = ['<|end_chronicle|>', '<|end_prophecy|>', '<|end_treaty|>',
                '<|end_letter|>', '<|endoftext|>']

    for tag in end_tags:
        if tag in generated_only:
            generated_only = generated_only.split(tag)[0].strip() + f"\n\n{tag}"
            break

    num_tokens = outputs.shape[1] - inputs["input_ids"].shape[1]
    tokens_per_sec = num_tokens / generation_time if generation_time > 0 else 0

    return {
        "generated": generated_only,
        "num_tokens": num_tokens,
        "generation_time": generation_time,
        "tokens_per_sec": tokens_per_sec
    }

def run_improved_tests(model, tokenizer, device):
    """Run improved test suite."""
    console.print(Panel.fit(
        "🧪 [bold blue]Improved Inference Test Suite[/bold blue]\n"
        "Better settings to avoid repetition",
        border_style="blue"
    ))

    test_cases = [
        {
            "name": "Chronicle",
            "prompt": "<|chronicle|>\nTitle: The Battle of Shadow Valley\nDate: Year 1262\nLocation: Shadow Valley\n\nThe forces of the Crystal Spire met their adversaries at dawn. Commander Marcus led the charge while..."
        },
        {
            "name": "Prophecy",
            "prompt": "<|prophecy|>\nSpoken by: Oracle Thane\nDate: Year 1268\n\nWhen three moons align and stars fall from the sky, the ancient powers will awaken. Those who seek the truth must journey to..."
        },
        {
            "name": "Treaty",
            "prompt": "<|treaty|>\nBetween: The Crystal Spire and Elderwood Council\nDate: Year 1270\n\nArticle I: Terms of Peace\n\nBoth parties agree to cease all hostilities and establish..."
        },
        {
            "name": "Letter",
            "prompt": "<|letter|>\nFrom: Scholar Aria\nTo: High Council\nDate: Year 1265\n\nHonorable Council Members,\n\nI write to inform you of a discovery in the ancient archives that may change our understanding of..."
        },
        {
            "name": "Journal Entry",
            "prompt": "<|journal|>\nAuthor: Explorer Kellan\nDate: Year 1263, Day 15\nLocation: The Obsidian Wastes\n\nDay 15: Today we found ruins that match the descriptions in the old texts. The structures are..."
        }
    ]

    results = []

    for i, test in enumerate(test_cases, 1):
        console.print(f"\n[bold cyan]Test {i}/{len(test_cases)}: {test['name']}[/bold cyan]")

        result = generate_text_improved(
            model,
            tokenizer,
            test['prompt'],
            max_new_tokens=200,
            device=device
        )

        console.print(Panel(
            result['generated'],
            title=f"[bold green]Generated {test['name']}[/bold green]",
            border_style="green"
        ))

        console.print(f"[dim]📊 {result['num_tokens']} tokens | {result['generation_time']:.1f}s | {result['tokens_per_sec']:.1f} tok/s[/dim]")

        results.append({
            "test_name": test['name'],
            "prompt": test['prompt'],
            "generated": result['generated'],
            "metrics": {
                "tokens": result['num_tokens'],
                "time": result['generation_time'],
                "tokens_per_sec": result['tokens_per_sec']
            }
        })

    return results

def main():
    """Main testing workflow."""
    console.print(Panel.fit(
        "🧪 [bold green]Improved Local Inference Testing[/bold green]\n\n"
        "Testing with optimized generation settings\n"
        "• Repetition penalty: 1.2\n"
        "• No repeat n-grams: 3\n"
        "• Temperature: 0.9\n"
        "• Auto-stop at end tags",
        border_style="green"
    ))

    try:
        device = setup_device()
        model, tokenizer = load_model(CHECKPOINT_PATH, device)
        results = run_improved_tests(model, tokenizer, device)

        # Save results
        output_file = OUTPUT_DIR / f"inference_improved_{int(time.time())}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump({
                "checkpoint": "checkpoint-5940",
                "timestamp": time.time(),
                "settings": {
                    "temperature": 0.9,
                    "repetition_penalty": 1.2,
                    "no_repeat_ngram_size": 3,
                    "max_new_tokens": 200
                },
                "results": results
            }, f, indent=2, ensure_ascii=False)

        console.print(f"\n💾 Results saved to: [bold]{output_file}[/bold]")

        # Summary
        avg_speed = sum(r['metrics']['tokens_per_sec'] for r in results) / len(results)

        console.print(Panel.fit(
            f"✨ [bold green]Testing Complete![/bold green]\n\n"
            f"Tests Run: {len(results)}\n"
            f"Avg Speed: {avg_speed:.1f} tokens/sec\n"
            f"Results: {output_file.name}\n\n"
            f"[bold]Quality Notes:[/bold]\n"
            f"• Improved settings reduce repetition\n"
            f"• Auto-stops at end tags\n"
            f"• Temperature 0.9 for variety",
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
