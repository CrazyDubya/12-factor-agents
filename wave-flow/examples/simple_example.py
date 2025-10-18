"""
Simple example demonstrating Conductor usage.

This example shows:
1. Creating a task
2. Setting up adapters
3. Planning execution
4. Running the task
5. Inspecting results
"""

import asyncio
import os
from conductor.envelopes import TaskEnvelope, TaskConstraints, PrivacyLevel
from conductor.adapters.base import ToolCapability, ExecutionEnvironment
from conductor.adapters.llm import LLMAdapter
from conductor.planner import Router, Planner
from conductor.executor import Executor


async def main():
    """Run a simple code explanation task."""

    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set")
        print("Set it with: export OPENAI_API_KEY=sk-...")
        return

    # Create task
    task = TaskEnvelope(
        id="example-1",
        intent="explain this Python code",
        inputs={
            "prompt": """Explain what this code does:

def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""
        },
        constraints=TaskConstraints(
            privacy=PrivacyLevel.EXTERNAL,
            budget_usd=0.10,
            deadline_ms=30000,  # 30 seconds
        ),
    )

    print("📋 Task created:")
    print(f"   Intent: {task.intent}")
    print(f"   Privacy: {task.constraints.privacy.value}")
    print(f"   Budget: ${task.constraints.budget_usd:.2f}")
    print()

    # Setup LLM adapter
    capability = ToolCapability(
        name="gpt-3.5-turbo",
        version="0.1.0",
        intents=["explain", "analyze", "code", "write"],
        input_modes=["api"],
        output_modes=["text"],
        token_limit=4096,
        rate_limit_rps=10.0,
        environments=[ExecutionEnvironment.CLOUD],
        privacy_compatible=[PrivacyLevel.EXTERNAL],
    )

    adapter = LLMAdapter(
        capability,
        config={
            "provider": "openai",
            "model": "gpt-3.5-turbo",
            "api_key": api_key,
        },
    )

    adapters = {"gpt-3.5-turbo": adapter}

    print("🔧 Adapters configured:")
    print(f"   - {adapter.get_name()} v{adapter.get_version()}")
    print()

    # Create router and planner
    router = Router(list(adapters.values()))
    planner = Planner(router)

    # Plan execution
    plan = planner.plan(task)

    if not plan:
        print("❌ Error: No tools can handle this task")
        return

    print("📐 Execution plan created:")
    print(f"   Strategy: {plan.metadata['strategy']}")
    print(f"   Tools: {plan.metadata['tool_count']}")
    print(f"   Top score: {plan.metadata['top_score']:.2f}")
    print()

    # Execute
    print("⚙️  Executing...")
    executor = Executor(adapters)
    results = await executor.execute_plan(plan)

    # Display results
    print()
    print("="*60)
    print("RESULTS")
    print("="*60)
    print()

    for node_id, result in results.items():
        print(f"Status: {result.status.value}")

        if result.error:
            print(f"❌ Error: {result.error}")
            continue

        if result.diagnostics:
            print(f"⏱️  Latency: {result.diagnostics.latency_ms:.0f}ms")
            print(f"💰 Cost: ${result.diagnostics.cost_usd:.4f}")
            if result.diagnostics.tokens_input:
                print(f"📊 Tokens: {result.diagnostics.tokens_input} in, {result.diagnostics.tokens_output} out")

        if result.artifacts:
            print()
            print("📄 Output:")
            print("-" * 60)
            for artifact in result.artifacts:
                print(artifact.content)
            print("-" * 60)

        print()

    # Budget summary
    budget_status = executor.get_budget_status()
    print(f"💰 Budget: ${budget_status['spent']:.4f} / ${budget_status['limit']:.2f}")
    print(f"   Remaining: ${budget_status['remaining']:.4f} ({100 - budget_status['percent_used']:.1f}%)")


if __name__ == "__main__":
    asyncio.run(main())
