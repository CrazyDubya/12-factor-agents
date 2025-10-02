#!/usr/bin/env python3
"""
Pre-flight Check for Local Testing
Verifies all dependencies and model files are ready
"""

import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

def check_imports():
    """Verify all required packages are installed."""
    console.print("\n[bold]1. Checking Python Packages...[/bold]")

    packages = {
        "torch": "PyTorch (deep learning)",
        "transformers": "Hugging Face Transformers",
        "peft": "Parameter-Efficient Fine-Tuning",
        "rich": "Terminal formatting"
    }

    results = []
    all_ok = True

    for package, description in packages.items():
        try:
            if package == "torch":
                import torch
                version = torch.__version__
            elif package == "transformers":
                import transformers
                version = transformers.__version__
            elif package == "peft":
                import peft
                version = peft.__version__
            elif package == "rich":
                import rich
                version = getattr(rich, "__version__", "installed")

            results.append((package, "✅", version, description))
        except ImportError:
            results.append((package, "❌", "Not installed", description))
            all_ok = False

    table = Table()
    table.add_column("Package", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Version", style="yellow")
    table.add_column("Purpose", style="dim")

    for row in results:
        table.add_row(*row)

    console.print(table)

    return all_ok

def check_device():
    """Check available compute devices."""
    console.print("\n[bold]2. Checking Compute Devices...[/bold]")

    try:
        import torch

        devices = []

        if torch.cuda.is_available():
            devices.append(("CUDA GPU", "✅", torch.cuda.get_device_name(0)))
        else:
            devices.append(("CUDA GPU", "❌", "Not available"))

        if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            devices.append(("Apple Silicon (MPS)", "✅", "Available"))
        else:
            devices.append(("Apple Silicon (MPS)", "❌", "Not available"))

        devices.append(("CPU", "✅", "Always available (slowest)"))

        table = Table()
        table.add_column("Device", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Details", style="yellow")

        for row in devices:
            table.add_row(*row)

        console.print(table)

        # Determine best device
        if torch.cuda.is_available():
            best = "CUDA GPU (fastest)"
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            best = "Apple Silicon MPS (good)"
        else:
            best = "CPU (slowest, but works)"

        console.print(f"\n💡 Will use: [bold green]{best}[/bold green]")

    except ImportError:
        console.print("[red]❌ Cannot check devices (torch not installed)[/red]")
        return False

    return True

def check_model_files():
    """Verify model files are present."""
    console.print("\n[bold]3. Checking Model Files...[/bold]")

    checkpoint_path = Path("models/ultra_narrative_a10/checkpoints/checkpoint-5940")

    required_files = [
        ("adapter_model.safetensors", "LoRA adapter weights"),
        ("adapter_config.json", "LoRA configuration"),
        ("tokenizer.json", "Tokenizer"),
        ("vocab.json", "Vocabulary"),
        ("merges.txt", "BPE merges"),
    ]

    results = []
    all_ok = True

    for filename, description in required_files:
        file_path = checkpoint_path / filename
        if file_path.exists():
            size = file_path.stat().st_size / (1024 * 1024)  # MB
            results.append((filename, "✅", f"{size:.1f} MB", description))
        else:
            results.append((filename, "❌", "Missing", description))
            all_ok = False

    table = Table()
    table.add_column("File", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Size", style="yellow")
    table.add_column("Purpose", style="dim")

    for row in results:
        table.add_row(*row)

    console.print(table)

    if all_ok:
        console.print(f"\n✅ Model location: [bold]{checkpoint_path}[/bold]")
    else:
        console.print(f"\n❌ Model incomplete at: [bold]{checkpoint_path}[/bold]")

    return all_ok

def check_other_checkpoints():
    """Check availability of other checkpoints."""
    console.print("\n[bold]4. Checking Other Checkpoints...[/bold]")

    base_path = Path("models/ultra_narrative_a10/checkpoints")
    checkpoints = ["checkpoint-1250", "checkpoint-2500", "checkpoint-3750", "checkpoint-5000"]

    results = []
    for checkpoint in checkpoints:
        ckpt_path = base_path / checkpoint
        if ckpt_path.exists() and (ckpt_path / "adapter_model.safetensors").exists():
            results.append((checkpoint, "✅", "Available"))
        else:
            results.append((checkpoint, "❌", "Missing"))

    table = Table()
    table.add_column("Checkpoint", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Details", style="yellow")

    for row in results:
        table.add_row(*row)

    console.print(table)

    available = sum(1 for _, status, _ in results if status == "✅")
    console.print(f"\n💡 {available}/{len(checkpoints)} earlier checkpoints available")
    console.print("   (Used by test_all_checkpoints.py to compare training progression)")

def check_test_scripts():
    """Verify test scripts are present."""
    console.print("\n[bold]5. Checking Test Scripts...[/bold]")

    scripts = [
        ("test_local_inference.py", "Quick 3-sample test"),
        ("test_all_checkpoints.py", "Compare all checkpoints"),
        ("batch_test_narratives.py", "Comprehensive 30-sample test"),
    ]

    results = []
    all_ok = True

    for script, description in scripts:
        script_path = Path(script)
        if script_path.exists():
            results.append((script, "✅", description))
        else:
            results.append((script, "❌", "Missing"))
            all_ok = False

    table = Table()
    table.add_column("Script", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Purpose", style="dim")

    for row in results:
        table.add_row(*row)

    console.print(table)

    return all_ok

def main():
    """Run all pre-flight checks."""
    console.print(Panel.fit(
        "🔍 [bold green]Pre-Flight Check[/bold green]\n\n"
        "Verifying setup for local inference testing",
        border_style="green"
    ))

    checks = {
        "Python Packages": check_imports(),
        "Compute Devices": check_device(),
        "Model Files": check_model_files(),
        "Test Scripts": check_test_scripts(),
    }

    # Optional check
    check_other_checkpoints()

    # Summary
    console.print("\n" + "=" * 60)
    console.print("\n[bold]📋 Pre-Flight Check Summary:[/bold]\n")

    all_passed = True
    for check_name, passed in checks.items():
        status = "✅" if passed else "❌"
        console.print(f"{status} {check_name}")
        if not passed:
            all_passed = False

    console.print("\n" + "=" * 60)

    if all_passed:
        console.print(Panel.fit(
            "✨ [bold green]All Checks Passed![/bold green]\n\n"
            "Ready for local testing. Run:\n\n"
            "  [bold cyan]python test_local_inference.py[/bold cyan]\n\n"
            "See TESTING_GUIDE.md for full instructions.",
            border_style="green"
        ))
        return 0
    else:
        console.print(Panel.fit(
            "❌ [bold red]Some Checks Failed[/bold red]\n\n"
            "Fix the issues above before testing.\n\n"
            "[bold]Common fixes:[/bold]\n"
            "• Missing packages: pip install torch transformers peft rich\n"
            "• Missing model: Re-download from Lambda server\n"
            "• Missing scripts: Re-run setup commands",
            border_style="red"
        ))
        return 1

if __name__ == "__main__":
    sys.exit(main())
