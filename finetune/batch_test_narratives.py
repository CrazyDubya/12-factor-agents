#!/usr/bin/env python3
"""
Batch Narrative Testing
Test all 10 document types from the training corpus
Generate multiple samples per type to evaluate model versatility
"""

import json
import time
from pathlib import Path
from datetime import datetime

import torch
from peft import PeftModel, PeftConfig
from transformers import AutoModelForCausalLM, AutoTokenizer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

CHECKPOINT_PATH = Path("models/ultra_narrative_a10/checkpoints/checkpoint-5940")
OUTPUT_DIR = Path("test_outputs/batch_narratives")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# All 10 document types from training corpus
NARRATIVE_TYPES = {
    "chronicle": {
        "prompts": [
            "<|chronicle|>\nTitle: The Fall of the Crystal Spire\nDate: Year 1261\nLocation: The Crystal Spire\n\n",
            "<|chronicle|>\nTitle: Discovery of the Ancient Portal\nDate: Year 1255\nLocation: Elderwood Forest\n\n",
            "<|chronicle|>\nTitle: The Great Council Meeting\nDate: Year 1268\nLocation: Harmonic Nexus\n\n"
        ]
    },
    "prophecy": {
        "prompts": [
            "<|prophecy|>\nSpoken by: Prophet Iris the Wise\nDate: Year 1257\n\nWhen the twin moons align, the ancient powers will...\n\n",
            "<|prophecy|>\nSpoken by: Seer Elara\nDate: Year 1263\n\nI have seen darkness rising from the north, bringing...\n\n",
            "<|prophecy|>\nSpoken by: Oracle Thane\nDate: Year 1269\n\nThree signs shall herald the coming age...\n\n"
        ]
    },
    "treaty": {
        "prompts": [
            "<|treaty|>\nBetween: The Crystal Spire and Shadow Collective\nDate: Year 1260\n\nArticle I: Territorial Boundaries\n\n",
            "<|treaty|>\nBetween: Elderwood Council and The Time Keepers\nDate: Year 1265\n\nArticle I: Terms of Alliance\n\n",
            "<|treaty|>\nBetween: Harmonic Nexus and Northern Tribes\nDate: Year 1270\n\nArticle I: Trade Agreements\n\n"
        ]
    },
    "letter": {
        "prompts": [
            "<|letter|>\nFrom: Commander Marcus\nTo: High Council\nDate: Year 1262\n\nEsteemed Council members, I write with urgent news from the front...\n\n",
            "<|letter|>\nFrom: Scholar Aria\nTo: Master Librarian\nDate: Year 1258\n\nDear Master, my research has uncovered...\n\n",
            "<|letter|>\nFrom: Ambassador Kellan\nTo: Queen Seraphina\nDate: Year 1266\n\nYour Majesty, negotiations have reached a critical juncture...\n\n"
        ]
    },
    "journal": {
        "prompts": [
            "<|journal|>\nAuthor: Explorer Thane\nDate: Year 1264, Day 42\nLocation: The Obsidian Wastes\n\nDay 42: We discovered ruins today that match the ancient texts...\n\n",
            "<|journal|>\nAuthor: Mage Iris\nDate: Year 1259, Winter Solstice\nLocation: Crystal Tower\n\nMy experiments with temporal magic have revealed...\n\n",
            "<|journal|>\nAuthor: Historian Marcus\nDate: Year 1267\nLocation: The Great Library\n\nToday I uncovered records that challenge everything we thought we knew...\n\n"
        ]
    },
    "report": {
        "prompts": [
            "<|report|>\nSubmitted by: Captain Elara\nTo: High Command\nDate: Year 1263\nSubject: Border Patrol Incident\n\nSummary: During routine patrol, our unit encountered...\n\n",
            "<|report|>\nSubmitted by: Chief Scientist Thane\nTo: Research Council\nDate: Year 1261\nSubject: Anomaly Detection\n\nFindings: Sensors detected unusual energy readings...\n\n",
            "<|report|>\nSubmitted by: Scout Commander Aria\nTo: War Council\nDate: Year 1268\nSubject: Enemy Movements\n\nIntelligence Report: Enemy forces have been observed...\n\n"
        ]
    },
    "decree": {
        "prompts": [
            "<|decree|>\nIssued by: Queen Seraphina\nDate: Year 1265\nSubject: Protection of Ancient Sites\n\nBy royal authority, it is hereby decreed that...\n\n",
            "<|decree|>\nIssued by: High Council\nDate: Year 1260\nSubject: Emergency Powers\n\nIn light of recent events, the Council declares...\n\n",
            "<|decree|>\nIssued by: Emperor Kellan\nDate: Year 1270\nSubject: New Trade Regulations\n\nLet it be known throughout the realm that...\n\n"
        ]
    },
    "speech": {
        "prompts": [
            "<|speech|>\nSpeaker: General Marcus\nOccasion: Victory Celebration\nDate: Year 1262\nLocation: Grand Plaza\n\nFellow citizens, today we celebrate not just a victory, but...\n\n",
            "<|speech|>\nSpeaker: High Priestess Iris\nOccasion: Festival of Light\nDate: Year 1266\nLocation: Temple of Stars\n\nGathered faithful, on this sacred day we remember...\n\n",
            "<|speech|>\nSpeaker: Chancellor Thane\nOccasion: Council Session\nDate: Year 1269\nLocation: Council Chambers\n\nHonorable members, the matter before us today requires...\n\n"
        ]
    },
    "legend": {
        "prompts": [
            "<|legend|>\nTitle: The First Guardian\nTold by: Elder Storytellers\nDate: Ancient Times\n\nIn the age before recorded history, when the world was young...\n\n",
            "<|legend|>\nTitle: The Crystal of Eternity\nTold by: Village Elders\nDate: Time Immemorial\n\nLong ago, before the great kingdoms rose, there existed a crystal of infinite power...\n\n",
            "<|legend|>\nTitle: The Shadow Wars\nTold by: Bardic Tradition\nDate: The Old Days\n\nOur ancestors speak of a time when darkness covered the land...\n\n"
        ]
    },
    "ritual": {
        "prompts": [
            "<|ritual|>\nName: The Binding Ceremony\nPerformed by: High Priest\nDate: Year 1264\nLocation: Sacred Grove\n\nPreparation: At dawn, gather the sacred herbs and...\n\n",
            "<|ritual|>\nName: The Summoning of Light\nPerformed by: Circle of Mages\nDate: Year 1267\nLocation: Power Nexus\n\nStep One: Form the circle at the cardinal points...\n\n",
            "<|ritual|>\nName: The Oath of Unity\nPerformed by: Council Members\nDate: Year 1270\nLocation: Unity Hall\n\nThe ceremony begins with each participant pledging...\n\n"
        ]
    }
}

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

def load_model(checkpoint_path: Path, device: torch.device):
    """Load the fine-tuned model."""
    console.print(f"\n📂 Loading model from: {checkpoint_path}")

    config = PeftConfig.from_pretrained(checkpoint_path)

    base_model = AutoModelForCausalLM.from_pretrained(
        config.base_model_name_or_path,
        torch_dtype=torch.float16 if device.type != "cpu" else torch.float32,
        device_map="auto",
        low_cpu_mem_usage=True
    )

    model = PeftModel.from_pretrained(base_model, checkpoint_path)
    model = model.to(device)
    model.eval()

    tokenizer = AutoTokenizer.from_pretrained(checkpoint_path)

    console.print("✅ Model loaded\n")

    return model, tokenizer

def generate_text(model, tokenizer, prompt: str, device: torch.device, max_tokens: int = 250):
    """Generate text from prompt."""
    inputs = tokenizer(prompt, return_tensors="pt")
    if device:
        inputs = {k: v.to(device) for k, v in inputs.items()}

    start_time = time.time()

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            temperature=0.8,
            top_p=0.9,
            do_sample=True,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )

    generation_time = time.time() - start_time
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    generated_only = generated_text[len(prompt):].strip()

    num_tokens = outputs.shape[1] - inputs["input_ids"].shape[1]

    return {
        "generated": generated_only,
        "tokens": num_tokens,
        "time": generation_time,
        "tokens_per_sec": num_tokens / generation_time if generation_time > 0 else 0
    }

def run_batch_tests(model, tokenizer, device):
    """Test all narrative types."""
    console.print(Panel.fit(
        f"🧪 [bold blue]Batch Narrative Testing[/bold blue]\n\n"
        f"Testing {len(NARRATIVE_TYPES)} document types\n"
        f"3 samples per type = {len(NARRATIVE_TYPES) * 3} total generations",
        border_style="blue"
    ))

    all_results = {}
    total_tests = sum(len(data["prompts"]) for data in NARRATIVE_TYPES.values())

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:

        task = progress.add_task(
            f"[cyan]Generating narratives...",
            total=total_tests
        )

        for narrative_type, data in NARRATIVE_TYPES.items():
            console.print(f"\n[bold cyan]Testing: {narrative_type.upper()}[/bold cyan]")

            type_results = []

            for i, prompt in enumerate(data["prompts"], 1):
                console.print(f"  Sample {i}/{len(data['prompts'])}...", end=" ")

                result = generate_text(model, tokenizer, prompt, device)

                console.print(f"[green]✓[/green] ({result['tokens']} tokens, {result['tokens_per_sec']:.1f} tok/s)")

                type_results.append({
                    "prompt": prompt,
                    "generated": result["generated"],
                    "metrics": {
                        "tokens": result["tokens"],
                        "time": result["time"],
                        "tokens_per_sec": result["tokens_per_sec"]
                    }
                })

                progress.update(task, advance=1)

            all_results[narrative_type] = type_results

    return all_results

def save_results(results):
    """Save batch test results."""
    timestamp = int(time.time())
    datetime_str = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save JSON
    json_file = OUTPUT_DIR / f"batch_narratives_{datetime_str}.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": timestamp,
            "checkpoint": "checkpoint-5940",
            "narrative_types": len(results),
            "total_samples": sum(len(samples) for samples in results.values()),
            "results": results
        }, f, indent=2, ensure_ascii=False)

    console.print(f"\n💾 JSON results: [bold]{json_file}[/bold]")

    # Create HTML report
    html_file = OUTPUT_DIR / f"batch_narratives_{datetime_str}.html"
    with open(html_file, "w", encoding="utf-8") as f:
        f.write("""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Batch Narrative Test Results</title>
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; max-width: 1200px; margin: 40px auto; padding: 20px; background: #f5f5f5; }
        h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
        .narrative-type { background: white; margin: 20px 0; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .narrative-type h2 { color: #3498db; margin-top: 0; }
        .sample { background: #f8f9fa; margin: 15px 0; padding: 15px; border-left: 4px solid #3498db; }
        .prompt { color: #7f8c8d; font-size: 0.9em; margin-bottom: 10px; font-style: italic; }
        .generated { white-space: pre-wrap; line-height: 1.6; }
        .metrics { color: #27ae60; font-size: 0.85em; margin-top: 10px; padding-top: 10px; border-top: 1px solid #ddd; }
    </style>
</head>
<body>
    <h1>📚 Batch Narrative Test Results</h1>
    <p><strong>Checkpoint:</strong> checkpoint-5940 (final)</p>
    <p><strong>Date:</strong> """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
    <p><strong>Narrative Types:</strong> """ + str(len(results)) + """</p>
    <p><strong>Total Samples:</strong> """ + str(sum(len(samples) for samples in results.values())) + """</p>
""")

        for narrative_type, samples in results.items():
            f.write(f'<div class="narrative-type">\n')
            f.write(f'<h2>📝 {narrative_type.upper()}</h2>\n')

            for i, sample in enumerate(samples, 1):
                f.write(f'<div class="sample">\n')
                f.write(f'<h3>Sample {i}</h3>\n')
                f.write(f'<div class="prompt">Prompt: {sample["prompt"][:100]}...</div>\n')
                f.write(f'<div class="generated">{sample["generated"][:500]}{"..." if len(sample["generated"]) > 500 else ""}</div>\n')
                f.write(f'<div class="metrics">🎯 {sample["metrics"]["tokens"]} tokens | ⏱️ {sample["metrics"]["time"]:.2f}s | 🚀 {sample["metrics"]["tokens_per_sec"]:.1f} tok/s</div>\n')
                f.write('</div>\n')

            f.write('</div>\n')

        f.write('</body>\n</html>')

    console.print(f"📄 HTML report: [bold]{html_file}[/bold]")

    return json_file, html_file

def main():
    """Main batch testing workflow."""
    console.print(Panel.fit(
        "📚 [bold green]Batch Narrative Testing[/bold green]\n\n"
        "Comprehensive evaluation of all narrative types\n"
        "A10 fine-tuned model on 10K documents",
        border_style="green"
    ))

    try:
        device = setup_device()
        model, tokenizer = load_model(CHECKPOINT_PATH, device)

        results = run_batch_tests(model, tokenizer, device)

        json_file, html_file = save_results(results)

        # Summary statistics
        total_samples = sum(len(samples) for samples in results.values())
        avg_tokens = sum(s["metrics"]["tokens"] for samples in results.values() for s in samples) / total_samples
        avg_speed = sum(s["metrics"]["tokens_per_sec"] for samples in results.values() for s in samples) / total_samples

        console.print(Panel.fit(
            f"✨ [bold green]Batch Testing Complete![/bold green]\n\n"
            f"📊 Statistics:\n"
            f"• Narrative Types: {len(results)}\n"
            f"• Total Samples: {total_samples}\n"
            f"• Avg Tokens/Sample: {avg_tokens:.0f}\n"
            f"• Avg Speed: {avg_speed:.1f} tokens/sec\n\n"
            f"📁 Output Files:\n"
            f"• JSON: {json_file.name}\n"
            f"• HTML: {html_file.name}\n\n"
            f"[bold]Open the HTML file in your browser to review all generated narratives![/bold]",
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
