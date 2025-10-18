"""
Main entry point for Conductor orchestration system.

Usage:
    conductor run <intent> [options]
    conductor serve [options]
    conductor status
"""

import asyncio
import sys
import argparse
import uuid
from pathlib import Path
from typing import Dict, List, Optional

from conductor.envelopes import (
    TaskEnvelope,
    TaskConstraints,
    PrivacyLevel,
)
from conductor.adapters.base import BaseAdapter, ToolCapability, ExecutionEnvironment
from conductor.adapters.cli import CLIAdapter
from conductor.adapters.http import HTTPAdapter
from conductor.adapters.llm import LLMAdapter
from conductor.adapters.wave_terminal import WaveTerminalAdapter, get_wave_terminal_capability
from conductor.planner import Router, Planner
from conductor.executor import Executor
from conductor.harvest import Harvester


def load_capabilities() -> Dict[str, ToolCapability]:
    """
    Load tool capabilities from YAML files.

    For MVP, create some defaults programmatically.
    """
    capabilities = {}

    # Default LLM capability
    capabilities["gpt-3.5-turbo"] = ToolCapability(
        name="gpt-3.5-turbo",
        version="0.1.0",
        intents=["code", "write", "analyze", "edit", "generate", "explain"],
        input_modes=["api"],
        output_modes=["text", "json"],
        token_limit=4096,
        rate_limit_rps=10.0,
        rate_limit_burst=20,
        environments=[ExecutionEnvironment.CLOUD],
        cost_per_call=0.002,
        requires_auth=True,
        privacy_compatible=[PrivacyLevel.EXTERNAL],
    )

    # Default CLI capability
    capabilities["python"] = ToolCapability(
        name="python",
        version="3.11",
        intents=["python", "script", "execute", "run"],
        input_modes=["cli", "files"],
        output_modes=["stdout", "files"],
        environments=[ExecutionEnvironment.LOCAL],
        privacy_compatible=[PrivacyLevel.INTERNAL, PrivacyLevel.EXTERNAL],
    )

    return capabilities


def create_adapters(config: Dict) -> Dict[str, BaseAdapter]:
    """Create adapter instances from configuration."""
    adapters = {}

    # LLM adapters
    if config.get("openai_api_key"):
        cap = ToolCapability(
            name="gpt-3.5-turbo",
            version="0.1.0",
            intents=["code", "write", "analyze", "edit", "generate", "explain", "test"],
            input_modes=["api"],
            output_modes=["text", "json"],
            token_limit=4096,
            rate_limit_rps=10.0,
            environments=[ExecutionEnvironment.CLOUD],
            privacy_compatible=[PrivacyLevel.EXTERNAL],
        )
        adapters["gpt-3.5-turbo"] = LLMAdapter(
            cap,
            config={
                "provider": "openai",
                "model": "gpt-3.5-turbo",
                "api_key": config.get("openai_api_key"),
            },
        )

    # CLI adapters
    for command in ["python", "node", "bash"]:
        cap = ToolCapability(
            name=command,
            version="1.0.0",
            intents=[command, "execute", "run", "script"],
            input_modes=["cli"],
            output_modes=["stdout"],
            environments=[ExecutionEnvironment.LOCAL],
            privacy_compatible=[PrivacyLevel.INTERNAL, PrivacyLevel.EXTERNAL],
        )
        adapters[command] = CLIAdapter(
            cap,
            config={
                "command": command,
                "allowed_commands": [command],
            },
        )

    # Wave Terminal adapter (if configured)
    if config.get("wave_terminal_enabled", False):
        wave_config = {
            "ws_url": config.get("wave_terminal_ws_url", "ws://localhost:8765"),
            "api_token": config.get("wave_terminal_api_token"),
            "terminal_id": config.get("wave_terminal_id", "default"),
            "connection_timeout": config.get("wave_terminal_timeout", 30)
        }
        
        cap = get_wave_terminal_capability()
        adapters["wave-terminal"] = WaveTerminalAdapter(
            cap,
            config=wave_config
        )

    return adapters


async def run_task(args, config: Dict):
    """Run a single task."""
    # Create task envelope
    task = TaskEnvelope(
        id=str(uuid.uuid4()),
        intent=args.intent,
        inputs=vars(args),
        constraints=TaskConstraints(
            privacy=PrivacyLevel(args.privacy) if args.privacy else PrivacyLevel.EXTERNAL,
            deadline_ms=args.deadline * 1000 if args.deadline else None,
            budget_usd=args.budget,
        ),
    )

    # Create adapters
    adapters = create_adapters(config)

    if not adapters:
        print("Error: No adapters configured. Set OPENAI_API_KEY or configure tools.", file=sys.stderr)
        return 1

    # Create router and planner
    router = Router(list(adapters.values()))
    planner = Planner(router)

    # Create plan
    plan = planner.plan(task)

    if not plan:
        print(f"Error: No tools can handle intent: {task.intent}", file=sys.stderr)
        return 1

    print(f"📋 Plan created: {plan.metadata['strategy']} strategy with {plan.metadata['tool_count']} tool(s)")

    # Execute plan
    executor = Executor(adapters)
    results = await executor.execute_plan(plan)

    # Display results
    for node_id, result in results.items():
        print(f"\n{'='*60}")
        print(f"Node: {node_id}")
        print(f"Status: {result.status.value}")

        if result.error:
            print(f"Error: {result.error}")

        if result.diagnostics:
            print(f"Latency: {result.diagnostics.latency_ms:.0f}ms")
            if result.diagnostics.cost_usd:
                print(f"Cost: ${result.diagnostics.cost_usd:.4f}")

        if result.artifacts:
            print(f"\nArtifacts ({len(result.artifacts)}):")
            for i, artifact in enumerate(result.artifacts):
                print(f"  [{i}] {artifact.type.value}")
                if artifact.content and len(artifact.content) < 500:
                    print(f"      {artifact.content[:500]}")
                elif artifact.content:
                    print(f"      {artifact.content[:500]}... (truncated)")

    # Budget summary
    budget_status = executor.get_budget_status()
    if budget_status["limit"]:
        print(f"\n💰 Budget: ${budget_status['spent']:.4f} / ${budget_status['limit']:.2f} ({budget_status['percent_used']:.1f}%)")

    return 0


async def serve_web_ui(args):
    """Start web UI server."""
    print("Starting web UI server...")
    print("Web UI not yet implemented - coming soon!")
    return 1


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Conductor - AI orchestration system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Run command
    run_parser = subparsers.add_parser("run", help="Run a task")
    run_parser.add_argument("intent", help="Task intent (what to do)")
    run_parser.add_argument("--repo", help="Repository path")
    run_parser.add_argument("--file", help="File to operate on")
    run_parser.add_argument("--with", dest="with_steps", help="Additional steps (comma-separated)")
    run_parser.add_argument("--deadline", type=int, help="Deadline in seconds")
    run_parser.add_argument("--budget", type=float, help="Budget in USD")
    run_parser.add_argument("--privacy", choices=["internal", "external"], default="external")
    run_parser.add_argument("--input", help="Input data/file")
    run_parser.add_argument("--steps", help="Processing steps (comma-separated)")

    # Serve command
    serve_parser = subparsers.add_parser("serve", help="Start web UI server")
    serve_parser.add_argument("--port", type=int, default=8000, help="Server port")
    serve_parser.add_argument("--host", default="127.0.0.1", help="Server host")

    # Status command
    status_parser = subparsers.add_parser("status", help="Show conductor status")

    args = parser.parse_args()

    # Load config
    import os
    config = {
        "openai_api_key": os.getenv("OPENAI_API_KEY"),
        "anthropic_api_key": os.getenv("ANTHROPIC_API_KEY"),
        "wave_terminal_enabled": os.getenv("WAVE_TERMINAL_ENABLED", "false").lower() == "true",
        "wave_terminal_ws_url": os.getenv("WAVE_TERMINAL_WS_URL"),
        "wave_terminal_api_token": os.getenv("WAVE_TERMINAL_API_TOKEN"),
        "wave_terminal_id": os.getenv("WAVE_TERMINAL_ID", "default"),
        "wave_terminal_timeout": int(os.getenv("WAVE_TERMINAL_TIMEOUT", "30")),
    }

    # Dispatch command
    if args.command == "run":
        return asyncio.run(run_task(args, config))
    elif args.command == "serve":
        return asyncio.run(serve_web_ui(args))
    elif args.command == "status":
        print("Conductor status:")
        print(f"  Adapters: {len(create_adapters(config))}")
        return 0
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
