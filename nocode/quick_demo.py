#!/usr/bin/env python3
"""Quick automated demo of the testing framework"""

import subprocess
import json
from datetime import datetime
from pathlib import Path

print("=" * 80)
print("QUICK DEMO: Testing Ollama qwen2.5:0.5b on 3 Reasoning Tasks")
print("=" * 80)
print()

# Test scenarios
tests = [
    {
        "id": "demo_reasoning_001",
        "domain": "reasoning",
        "prompt": "What comes next in this sequence? 2, 6, 12, 20, 30, ?",
        "expected": "42",
        "description": "Pattern completion test"
    },
    {
        "id": "demo_reasoning_002",
        "domain": "reasoning",
        "prompt": "Given: All managers attend the weekly meeting. Sarah attends the weekly meeting. John is a manager. Can we conclude that Sarah is a manager? Explain briefly.",
        "expected": "No/Cannot conclude",
        "description": "Logical deduction test"
    },
    {
        "id": "demo_communication_001",
        "domain": "communication",
        "prompt": "Explain what a REST API is to someone with no technical background in 2-3 sentences.",
        "expected": "Simple explanation",
        "description": "Clear communication test"
    }
]

results = []
model = "qwen2.5:0.5b"

for i, test in enumerate(tests, 1):
    print(f"\n[Test {i}/3] {test['id']}")
    print(f"Domain: {test['domain']}")
    print(f"Description: {test['description']}")
    print(f"\nPrompt: {test['prompt']}")
    print("\nQuerying model...")

    # Query Ollama
    try:
        result = subprocess.run(
            ['ollama', 'run', model, test['prompt']],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            response = result.stdout.strip()
            print(f"\nModel Response:\n{'-'*60}")
            print(response[:500] + "..." if len(response) > 500 else response)
            print('-'*60)

            # Simple auto-evaluation
            status = "pass"  # Simplified for demo
            if test['expected'].lower() in response.lower():
                status = "pass"
                print(f"✓ AUTO-EVAL: PASS (found expected '{test['expected']}')")
            else:
                status = "partial"
                print(f"~ AUTO-EVAL: PARTIAL")

            results.append({
                "test_id": test['id'],
                "domain": test['domain'],
                "status": status,
                "agent_response": response,
                "timestamp": datetime.now().isoformat()
            })
        else:
            print(f"✗ Error: {result.stderr}")
            results.append({
                "test_id": test['id'],
                "domain": test['domain'],
                "status": "error",
                "agent_response": result.stderr,
                "timestamp": datetime.now().isoformat()
            })

    except Exception as e:
        print(f"✗ Error: {e}")
        results.append({
            "test_id": test['id'],
            "domain": test['domain'],
            "status": "error",
            "agent_response": str(e),
            "timestamp": datetime.now().isoformat()
        })

    print()

# Summary
print("=" * 80)
print("DEMO COMPLETE")
print("=" * 80)
passed = sum(1 for r in results if r['status'] == 'pass')
partial = sum(1 for r in results if r['status'] == 'partial')
failed = sum(1 for r in results if r['status'] in ['fail', 'error'])

print(f"\nResults: {passed} passed, {partial} partial, {failed} failed")
print(f"Success Rate: {(passed + partial * 0.5) / len(results) * 100:.1f}%")

# Save results
output_data = {
    "metadata": {
        "agent_name": f"Demo-Ollama-{model}",
        "start_time": datetime.now().isoformat(),
        "mode": "automated-demo",
        "total_tests": len(results),
        "pass_count": passed,
        "partial_count": partial,
        "fail_count": failed
    },
    "results": results
}

Path("test_results").mkdir(exist_ok=True)
output_file = Path("test_results") / f"demo_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

with open(output_file, 'w') as f:
    json.dump(output_data, f, indent=2)

print(f"\nResults saved to: {output_file}")
print(f"\nGenerate report: python3 generate_report.py {output_file}")
print("\nThis was a quick demo. For full testing:")
print("  python3 test_ollama_model.py --model qwen-128k --domain reasoning")
print()
