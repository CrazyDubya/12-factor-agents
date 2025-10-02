#!/usr/bin/env python3
"""
Quantitative Comparison: Base Model vs Fine-Tuned Model
Direct A/B comparison with same prompts
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

def load_base_model(device):
    """Load the BASE model (not fine-tuned)."""
    console.print("📂 Loading BASE model (Qwen2-1.5B-Instruct)...")
    start = time.time()

    model = AutoModelForCausalLM.from_pretrained(
        "Qwen/Qwen2-1.5B-Instruct",
        dtype=torch.float16 if device.type != "cpu" else torch.float32,
        device_map="auto",
        low_cpu_mem_usage=True
    )
    model.eval()

    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2-1.5B-Instruct")

    console.print(f"✅ Base model loaded in {time.time()-start:.1f}s\n")
    return model, tokenizer

def load_finetuned_model(device):
    """Load the FINE-TUNED model."""
    console.print("📂 Loading FINE-TUNED model (with LoRA adapters)...")
    start = time.time()

    config = PeftConfig.from_pretrained(CHECKPOINT_PATH)
    base_model = AutoModelForCausalLM.from_pretrained(
        config.base_model_name_or_path,
        dtype=torch.float16 if device.type != "cpu" else torch.float32,
        device_map="auto",
        low_cpu_mem_usage=True
    )

    model = PeftModel.from_pretrained(base_model, CHECKPOINT_PATH)
    model.eval()

    tokenizer = AutoTokenizer.from_pretrained(CHECKPOINT_PATH)

    console.print(f"✅ Fine-tuned model loaded in {time.time()-start:.1f}s\n")
    return model, tokenizer

def generate_text(model, tokenizer, prompt, device, max_tokens=200):
    """Generate text from a prompt."""
    inputs = tokenizer(prompt, return_tensors="pt")
    if device:
        inputs = {k: v.to(device) for k, v in inputs.items()}

    start = time.time()

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            temperature=0.7,
            top_p=0.9,
            do_sample=True,
            repetition_penalty=1.1,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )

    gen_time = time.time() - start
    full_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    generated = full_text[len(prompt):].strip()

    return {
        "text": generated,
        "time": gen_time,
        "tokens": len(tokenizer.encode(generated))
    }

def main():
    console.print(Panel.fit(
        "🔬 [bold green]BASE vs FINE-TUNED Comparison[/bold green]\n\n"
        "Objective A/B test with identical prompts",
        border_style="green"
    ))

    test_prompts = [
        "<|chronicle|>\nIn the year 1262, significant events transpired at Crystal Spire",
        "<|prophecy|>\nWhen the stars align and ancient powers awaken",
        "<|treaty|>\nBetween the forces of Crystal Spire and Elderwood"
    ]

    try:
        device = setup_device()
        console.print(f"Device: [cyan]{device}[/cyan]\n")

        base_model, base_tokenizer = load_base_model(device)
        ft_model, ft_tokenizer = load_finetuned_model(device)

        results = []

        for i, prompt in enumerate(test_prompts, 1):
            console.print(f"\n{'='*70}")
            console.print(f"[bold]TEST {i}/3: {prompt[:50]}...[/bold]")
            console.print('='*70)

            console.print("\n[yellow]BASE model:[/yellow]")
            base_result = generate_text(base_model, base_tokenizer, prompt, device)
            console.print(base_result['text'][:300])
            console.print(f"[dim]{base_result['tokens']} tokens, {base_result['time']:.1f}s[/dim]")

            console.print("\n[green]FINE-TUNED model:[/green]")
            ft_result = generate_text(ft_model, ft_tokenizer, prompt, device)
            console.print(ft_result['text'][:300])
            console.print(f"[dim]{ft_result['tokens']} tokens, {ft_result['time']:.1f}s[/dim]")

            results.append({
                "prompt": prompt,
                "base": base_result,
                "finetuned": ft_result
            })

        output_file = OUTPUT_DIR / f"comparison_{int(time.time())}.json"
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)

        console.print(f"\n\n💾 Saved to: {output_file}")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
