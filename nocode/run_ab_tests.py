#!/usr/bin/env python3
"""
A/B Testing Runner for Agent Improvement Experiments

Runs multiple prompt variants and compares results
"""

import subprocess
import json
import yaml
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict

# Prompt modification strategies
class PromptStrategy:
    """Base class for prompt modification strategies"""

    def modify_prompt(self, prompt: str, test_type: str) -> str:
        return prompt

class BaselineStrategy(PromptStrategy):
    """No modifications - control group"""
    name = "baseline"

class CoTStrategy(PromptStrategy):
    """Chain-of-Thought prompting"""
    name = "cot"

    def modify_prompt(self, prompt: str, test_type: str) -> str:
        if test_type in ['reasoning', 'analysis', 'planning']:
            return f"{prompt}\n\nLet's think through this step-by-step:\n1) First, identify what we know\n2) Then, apply logical reasoning\n3) Finally, state our conclusion clearly"
        return prompt

class FewShotStrategy(PromptStrategy):
    """Few-shot learning with examples"""
    name = "few_shot"

    EXAMPLES = {
        'communication': """Here are examples of clear explanations:

Example 1:
Q: Explain what a database is to someone non-technical.
A: A database is like a digital filing cabinet. Just as you organize papers in folders and drawers, a database organizes information in tables and categories, making it easy to find and update what you need.

Example 2:
Q: Explain cloud computing simply.
A: Cloud computing is like renting instead of owning. Rather than buying your own computers and storage, you rent computing power from companies over the internet, paying only for what you use.

Now your turn:
""",
        'content': """Here are examples of good content:

Example:
Q: Write a brief product benefit statement.
A: Our software saves teams 10+ hours per week by automating repetitive tasks, letting them focus on creative work that matters.

Now your turn:
""",
        'reasoning': """Here's how to approach reasoning:

Example:
Q: If all cats are mammals, and Fluffy is a cat, is Fluffy a mammal?
A: Yes. Using deductive logic:
   Premise 1: All cats are mammals
   Premise 2: Fluffy is a cat
   Conclusion: Therefore, Fluffy is a mammal

Now your turn:
"""
    }

    def modify_prompt(self, prompt: str, test_type: str) -> str:
        example = self.EXAMPLES.get(test_type, "")
        if example:
            return f"{example}\n{prompt}"
        return prompt

class StructuredOutputStrategy(PromptStrategy):
    """Explicit structure instructions"""
    name = "structured"

    def modify_prompt(self, prompt: str, test_type: str) -> str:
        structure = "\n\nFormat your response with:\n1. Brief overview\n2. Key details\n3. Conclusion/Answer"
        return f"{prompt}{structure}"

def run_variant_test(model: str, strategy: PromptStrategy, temperature: float = 0.7) -> Path:
    """Run tests with a specific variant"""

    print(f"\n{'='*80}")
    print(f"Running Variant: {strategy.name.upper()} (temp={temperature})")
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
                tests = data.get('tests', [])[:3]  # First 3 from each
                for test in tests:
                    test['domain'] = domain_file
                    if not test.get('context_files'):
                        all_tests.append(test)

    results = []

    for i, test in enumerate(all_tests, 1):
        test_id = test.get('id')
        domain = test.get('domain')
        prompt = test.get('prompt', '')

        # Apply strategy modification
        modified_prompt = strategy.modify_prompt(prompt, domain)

        print(f"[{i}/{len(all_tests)}] {test_id}")
        print(f"  Strategy: {strategy.name}")

        # Query Ollama with modified prompt and temperature
        try:
            cmd = ['ollama', 'run', model]
            # Note: ollama CLI doesn't support --temperature, this is for demonstration
            # In production, use Ollama API with temperature parameter
            result = subprocess.run(
                cmd + [modified_prompt],
                capture_output=True,
                text=True,
                timeout=45
            )

            response = result.stdout.strip() if result.returncode == 0 else f"ERROR: {result.stderr}"

            # Simple evaluation using regex patterns
            validation = test.get('validation', {})
            patterns = validation.get('response_patterns', [])
            matches = sum(1 for p in patterns if re.search(p, response, re.IGNORECASE))
            score = matches / len(patterns) if patterns else 0

            status = 'pass' if score >= 0.8 else 'partial' if score >= 0.5 else 'fail'

            print(f"  Result: {status.upper()} ({matches}/{len(patterns)} patterns)")

            results.append({
                "test_id": test_id,
                "domain": domain,
                "status": status,
                "score": matches,
                "max_score": len(patterns),
                "variant": strategy.name,
                "temperature": temperature,
                "modified_prompt_preview": modified_prompt[:200] + "...",
                "agent_response": response[:500] + "..." if len(response) > 500 else response,
                "timestamp": datetime.now().isoformat()
            })

        except Exception as e:
            print(f"  Error: {e}")
            continue

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = Path("test_results") / f"ab_test_{strategy.name}_temp{temperature}_{timestamp}.json"

    metadata = {
        "variant": strategy.name,
        "temperature": temperature,
        "model": model,
        "total_tests": len(results),
        "pass_count": sum(1 for r in results if r['status'] == 'pass'),
        "partial_count": sum(1 for r in results if r['status'] == 'partial'),
        "fail_count": sum(1 for r in results if r['status'] == 'fail'),
    }
    metadata["success_rate"] = (
        (metadata["pass_count"] + metadata["partial_count"] * 0.5) /
        metadata["total_tests"] * 100
        if metadata["total_tests"] > 0 else 0
    )

    with open(output_file, 'w') as f:
        json.dump({"metadata": metadata, "results": results}, f, indent=2)

    print(f"\n✓ Variant results saved: {output_file}")
    print(f"  Success rate: {metadata['success_rate']:.1f}%")

    return output_file

def compare_variants(result_files: List[Path]):
    """Compare results across variants"""

    print(f"\n{'='*80}")
    print("A/B TEST COMPARISON")
    print(f"{'='*80}\n")

    variants = []
    for file in result_files:
        with open(file, 'r') as f:
            data = json.load(f)
            variants.append(data['metadata'])

    # Sort by success rate
    variants.sort(key=lambda x: x['success_rate'], reverse=True)

    print(f"{'Variant':<20} {'Temp':<6} {'Tests':<6} {'Pass':<6} {'Success Rate':<15}")
    print("-" * 70)

    baseline = None
    for v in variants:
        if v['variant'] == 'baseline':
            baseline = v

        print(f"{v['variant']:<20} {v['temperature']:<6.1f} {v['total_tests']:<6} "
              f"{v['pass_count']:<6} {v['success_rate']:>6.1f}%")

    # Calculate improvements over baseline
    if baseline:
        print(f"\n{'='*80}")
        print("IMPROVEMENTS OVER BASELINE")
        print(f"{'='*80}\n")

        baseline_rate = baseline['success_rate']

        for v in variants:
            if v['variant'] != 'baseline':
                improvement = v['success_rate'] - baseline_rate
                rel_improvement = (improvement / baseline_rate * 100) if baseline_rate > 0 else 0

                symbol = "✓" if improvement > 5 else "~" if improvement > 0 else "✗"
                print(f"{symbol} {v['variant']:<20} {improvement:>+6.1f}% absolute "
                      f"({rel_improvement:>+6.1f}% relative)")

        print(f"\n{'='*80}")
        print("RECOMMENDATIONS")
        print(f"{'='*80}\n")

        best = variants[0]
        if best['variant'] != 'baseline' and best['success_rate'] - baseline_rate > 5:
            print(f"✓ RECOMMENDED: Use '{best['variant']}' variant")
            print(f"  Provides {best['success_rate'] - baseline_rate:.1f}% improvement")
            print(f"  Best for: {get_variant_use_cases(best['variant'])}")
        else:
            print(f"~ NO CLEAR WINNER: Improvements <5%")
            print(f"  Baseline performance is adequate")
            print(f"  Consider testing other improvement strategies")

def get_variant_use_cases(variant: str) -> str:
    """Get use case description for variant"""
    use_cases = {
        'cot': 'Reasoning, logic, multi-step problems',
        'few_shot': 'Unfamiliar formats, style matching, consistency',
        'structured': 'Reports, documentation, organized outputs'
    }
    return use_cases.get(variant, 'General use')

def main():
    print("="*80)
    print("A/B TESTING SUITE FOR AGENT IMPROVEMENT")
    print("="*80)

    model = "qwen2.5:3b"

    # Define test variants
    variants_to_test = [
        (BaselineStrategy(), 0.7),
        (CoTStrategy(), 0.5),
        (FewShotStrategy(), 0.7),
        (StructuredOutputStrategy(), 0.7),
    ]

    print(f"\nTesting {len(variants_to_test)} variants on model: {model}")
    print("\nVariants:")
    for strategy, temp in variants_to_test:
        print(f"  - {strategy.name} (temperature: {temp})")

    print("\nStarting tests (this will take several minutes)...")

    result_files = []
    for strategy, temperature in variants_to_test:
        result_file = run_variant_test(model, strategy, temperature)
        result_files.append(result_file)

    # Compare results
    compare_variants(result_files)

    print(f"\n{'='*80}")
    print("A/B TESTING COMPLETE")
    print(f"{'='*80}\n")
    print(f"Results saved in: test_results/ab_test_*.json")
    print(f"\nNext steps:")
    print(f"  1. Review variant performance above")
    print(f"  2. Implement winning strategy for production")
    print(f"  3. Re-run comprehensive tests with best variant")

if __name__ == "__main__":
    main()
