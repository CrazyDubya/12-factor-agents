#!/usr/bin/env python3
"""
Ollama Model Tester - Wrapper for testing Ollama models with the agent tester framework

Usage:
    python test_ollama_model.py --model qwen-128k --agent-name "Ollama-Qwen-128k"
    python test_ollama_model.py --model llama3.2 --domain research
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime


class OllamaModelTester:
    """Wrapper to test Ollama models through the agent testing framework"""

    def __init__(self, model_name: str, agent_name: str = None):
        self.model_name = model_name
        self.agent_name = agent_name or f"Ollama-{model_name}"
        self.results = []

    def query_model(self, prompt: str) -> str:
        """Query the Ollama model with a prompt"""
        try:
            # Call Ollama CLI
            result = subprocess.run(
                ['ollama', 'run', self.model_name, prompt],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return f"Error: {result.stderr}"

        except subprocess.TimeoutExpired:
            return "Error: Request timed out (60s limit)"
        except FileNotFoundError:
            return "Error: Ollama not found. Is it installed?"
        except Exception as e:
            return f"Error: {str(e)}"

    def check_model_available(self) -> bool:
        """Check if the model is available locally"""
        try:
            result = subprocess.run(
                ['ollama', 'list'],
                capture_output=True,
                text=True
            )

            return self.model_name in result.stdout

        except Exception:
            return False

    def run_interactive_test(self, domain: str = None):
        """Run the test framework in interactive mode with Ollama responses"""
        print(f"\n{'='*80}")
        print(f"Ollama Model Tester - {self.agent_name}")
        print(f"Model: {self.model_name}")
        print(f"{'='*80}\n")

        # Check if model is available
        if not self.check_model_available():
            print(f"❌ Model '{self.model_name}' not found locally.")
            print(f"   Run: ollama pull {self.model_name}")
            sys.exit(1)

        print(f"✓ Model '{self.model_name}' found")
        print(f"\nThis script will:")
        print(f"1. Show you each test prompt")
        print(f"2. Query the Ollama model automatically")
        print(f"3. Display the model's response")
        print(f"4. Ask you to evaluate the response")
        print(f"\nStarting in 3 seconds...")

        import time
        time.sleep(3)

        # Load test scenarios
        from agent_tester import AgentTester, TestMode

        tester = AgentTester(mode=TestMode.INTERACTIVE)
        tester.session_metadata['agent_name'] = self.agent_name
        tester.load_evaluation_criteria()

        scenarios = tester.load_test_scenarios(domain=domain)

        if not scenarios:
            print("❌ No test scenarios found!")
            sys.exit(1)

        print(f"\nLoaded {len(scenarios)} test scenarios")

        # Filter scenarios suitable for Ollama (no file operations)
        suitable_scenarios = [
            s for s in scenarios
            if not s.get('context_files') and  # No file reading required
            s.get('domain') not in ['multitool']  # Skip multi-tool tests
        ]

        print(f"Found {len(suitable_scenarios)} scenarios suitable for Ollama")
        print("\nNote: Skipping tests that require file operations or tool use\n")

        time.sleep(2)

        # Run tests
        for i, test in enumerate(suitable_scenarios, 1):
            print(f"\n{'='*80}")
            print(f"Test {i}/{len(suitable_scenarios)}: {test.get('id')}")
            print(f"Domain: {test.get('domain')}")
            print(f"{'='*80}\n")

            prompt = test.get('prompt', '')
            print(f"Prompt:\n{prompt}\n")

            print("Querying Ollama... (this may take a moment)")
            response = self.query_model(prompt)

            print(f"\n--- Model Response ---")
            print(response)
            print(f"--- End Response ---\n")

            # Save response for evaluation
            input("Press Enter to evaluate this response...")

            # Manual evaluation
            result = tester.evaluate_test_interactive(test, response)
            tester.test_results.append(result)

            # Update counters
            tester.session_metadata['total_tests'] += 1
            status = result['status']
            if status == 'pass':
                tester.session_metadata['pass_count'] += 1
            elif status == 'fail':
                tester.session_metadata['fail_count'] += 1
            elif status == 'partial':
                tester.session_metadata['partial_count'] += 1
            elif status == 'refused':
                tester.session_metadata['refused_count'] += 1
            elif status == 'error':
                tester.session_metadata['error_count'] += 1

        # Update session metadata
        tester.session_metadata['end_time'] = datetime.now().isoformat()

        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_agent_name = self.agent_name.lower().replace(' ', '_').replace('-', '_')
        output_file = f"test_results_{safe_agent_name}_{timestamp}.json"

        results_path = tester.save_results(filename=output_file)

        # Display summary
        tester.display_summary()

        print(f"\n{'='*80}")
        print(f"Testing Complete!")
        print(f"Results saved to: {results_path}")
        print(f"\nGenerate HTML report:")
        print(f"  python generate_report.py {results_path}")
        print(f"{'='*80}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Test Ollama models with the agent testing framework"
    )

    parser.add_argument(
        '--model',
        type=str,
        required=True,
        help='Ollama model name (e.g., qwen-128k, llama3.2, gemma2:9b)'
    )

    parser.add_argument(
        '--agent-name',
        type=str,
        help='Custom name for the agent in results (default: Ollama-{model})'
    )

    parser.add_argument(
        '--domain',
        type=str,
        help='Test only specific domain (e.g., research, reasoning, content)'
    )

    parser.add_argument(
        '--list-models',
        action='store_true',
        help='List available Ollama models'
    )

    args = parser.parse_args()

    if args.list_models:
        print("Available Ollama models:\n")
        subprocess.run(['ollama', 'list'])
        print("\nRecommended models for testing:")
        print("  - qwen-128k (best long-context)")
        print("  - llama3.2:latest (general purpose)")
        print("  - gemma2:9b (balanced)")
        sys.exit(0)

    # Create tester and run
    tester = OllamaModelTester(
        model_name=args.model,
        agent_name=args.agent_name
    )

    tester.run_interactive_test(domain=args.domain)


if __name__ == "__main__":
    main()
