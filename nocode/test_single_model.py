#!/usr/bin/env python3
"""
Test a single model with comprehensive suite
"""

import sys
import subprocess
import json
import yaml
from datetime import datetime
from pathlib import Path
import re

def test_model(model_name):
    """Run comprehensive tests on specified model"""

    print(f"\n{'='*80}")
    print(f"Testing: {model_name}")
    print(f"{'='*80}\n")

    # Load test scenarios
    scenarios_dir = Path("test_scenarios")
    domains_to_test = ['reasoning', 'communication']

    all_tests = []
    for domain_file in domains_to_test:
        yaml_file = scenarios_dir / f"{domain_file}_scenarios.yaml"
        if yaml_file.exists():
            with open(yaml_file, 'r') as f:
                data = yaml.safe_load(f)
                tests = data.get('tests', [])[:4]  # First 4 from each domain
                for test in tests:
                    test['domain'] = domain_file
                    all_tests.append(test)

    results = []
    passed = 0
    partial = 0
    failed = 0

    for i, test in enumerate(all_tests, 1):
        test_id = test.get('id')
        domain = test.get('domain')
        prompt = test.get('prompt', '')

        print(f"[{i}/{len(all_tests)}] {test_id}")

        # Query Ollama
        try:
            result = subprocess.run(
                ['ollama', 'run', model_name, prompt],
                capture_output=True,
                text=True,
                timeout=60
            )

            response = result.stdout.strip() if result.returncode == 0 else f"ERROR: {result.stderr}"

            # Validation
            validation = test.get('validation', {})
            patterns = validation.get('response_patterns', [])
            matches = sum(1 for p in patterns if re.search(p, response, re.IGNORECASE))
            score = matches / len(patterns) if patterns else 0

            status = 'pass' if score >= 0.8 else 'partial' if score >= 0.5 else 'fail'

            if status == 'pass':
                passed += 1
            elif status == 'partial':
                partial += 1
            else:
                failed += 1

            print(f"  Result: {status.upper()} ({matches}/{len(patterns)} patterns)")

            results.append({
                "test_id": test_id,
                "domain": domain,
                "status": status,
                "score": matches,
                "max_score": len(patterns),
                "pass_rate": score * 100,
                "agent_response": response,
                "full_response_length": len(response),
                "validation_details": {
                    f"pattern_{p}": "✓ Found" if re.search(p, response, re.IGNORECASE) else "✗ Missing"
                    for p in patterns
                },
                "quality_score": 4 if len(response) > 100 else 3,
                "timestamp": datetime.now().isoformat()
            })

        except Exception as e:
            print(f"  Error: {e}")
            failed += 1
            continue

    # Calculate success rate
    total = len(results)
    success_rate = ((passed + partial * 0.5) / total * 100) if total > 0 else 0

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_model_name = model_name.replace(':', '_').replace('/', '_')
    output_file = Path("test_results") / f"test_results_{safe_model_name}_{timestamp}.json"

    metadata = {
        "agent_name": f"Ollama-{model_name}",
        "start_time": datetime.now().isoformat(),
        "mode": "automated-multi-model",
        "total_tests": total,
        "pass_count": passed,
        "partial_count": partial,
        "fail_count": failed,
        "refused_count": 0,
        "success_rate": success_rate,
        "average_quality_score": sum(r.get('quality_score', 0) for r in results) / total if total > 0 else 0
    }

    with open(output_file, 'w') as f:
        json.dump({"metadata": metadata, "results": results}, f, indent=2)

    print(f"\n✓ Results saved: {output_file}")
    print(f"  Success rate: {success_rate:.1f}%")
    print(f"  Passed: {passed}, Partial: {partial}, Failed: {failed}")

    return output_file

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 test_single_model.py <model_name>")
        sys.exit(1)

    test_model(sys.argv[1])
