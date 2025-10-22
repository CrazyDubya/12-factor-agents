#!/usr/bin/env python3
"""
Agentic CLI Non-Coding Capability Tester

A comprehensive testing framework for evaluating AI agents on non-coding tasks
including research, analysis, planning, reasoning, and boundary testing.

Usage:
    python agent_tester.py --mode interactive
    python agent_tester.py --mode automated --domain research
    python agent_tester.py --compare agent1.json agent2.json
"""

import argparse
import json
import yaml
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from enum import Enum
import re


class TestMode(Enum):
    """Test execution modes"""
    INTERACTIVE = "interactive"  # Human-in-loop validation
    AUTOMATED = "automated"      # Programmatic evaluation
    HYBRID = "hybrid"            # Automated + human override


class TestStatus(Enum):
    """Test result status"""
    PASS = "pass"
    FAIL = "fail"
    PARTIAL = "partial"
    REFUSED = "refused"
    ERROR = "error"
    SKIPPED = "skipped"


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    MAGENTA = '\033[0;35m'
    NC = '\033[0m'  # No Color
    BOLD = '\033[1m'


class AgentTester:
    """Main test orchestrator for evaluating agentic CLI capabilities"""

    def __init__(self, mode: TestMode = TestMode.INTERACTIVE):
        self.mode = mode
        self.base_dir = Path(__file__).parent
        self.scenarios_dir = self.base_dir / "test_scenarios"
        self.data_dir = self.base_dir / "test_data"
        self.results_dir = self.base_dir / "test_results"
        self.evaluation_criteria = {}

        # Test tracking
        self.current_test = None
        self.test_results = []
        self.session_metadata = {
            "start_time": datetime.now().isoformat(),
            "mode": mode.value,
            "agent_name": "unknown",
            "total_tests": 0,
            "pass_count": 0,
            "fail_count": 0,
            "partial_count": 0,
            "refused_count": 0,
            "error_count": 0,
            "skipped_count": 0
        }

        # Ensure directories exist
        self._setup_directories()

    def _setup_directories(self):
        """Create necessary directories if they don't exist"""
        self.scenarios_dir.mkdir(exist_ok=True)
        self.data_dir.mkdir(exist_ok=True)
        self.results_dir.mkdir(exist_ok=True)

    def load_evaluation_criteria(self, criteria_file: str = "evaluation_criteria.yaml"):
        """Load evaluation criteria from YAML file"""
        criteria_path = self.base_dir / criteria_file
        if criteria_path.exists():
            with open(criteria_path, 'r') as f:
                self.evaluation_criteria = yaml.safe_load(f)
        else:
            print(f"{Colors.YELLOW}Warning: No evaluation criteria file found at {criteria_path}{Colors.NC}")
            self.evaluation_criteria = {}

    def load_test_scenarios(self, domain: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Load test scenarios from YAML files

        Args:
            domain: Optional domain filter (e.g., 'research', 'analysis')

        Returns:
            List of test scenario dictionaries
        """
        scenarios = []

        if not self.scenarios_dir.exists():
            print(f"{Colors.RED}Error: Test scenarios directory not found{Colors.NC}")
            return scenarios

        # Find all YAML scenario files
        pattern = f"{domain}_*.yaml" if domain else "*.yaml"
        scenario_files = list(self.scenarios_dir.glob(pattern))

        for scenario_file in sorted(scenario_files):
            try:
                with open(scenario_file, 'r') as f:
                    data = yaml.safe_load(f)
                    if 'tests' in data:
                        for test in data['tests']:
                            test['domain'] = data.get('domain', 'unknown')
                            test['source_file'] = scenario_file.name
                            scenarios.append(test)
            except Exception as e:
                print(f"{Colors.RED}Error loading {scenario_file}: {e}{Colors.NC}")

        return scenarios

    def display_test_prompt(self, test: Dict[str, Any]):
        """Display test prompt to user in interactive mode"""
        print(f"\n{Colors.CYAN}{'='*80}{Colors.NC}")
        print(f"{Colors.BOLD}Test ID: {test.get('id', 'unknown')}{Colors.NC}")
        print(f"{Colors.BOLD}Domain: {test.get('domain', 'unknown')}{Colors.NC}")
        print(f"{Colors.BOLD}Difficulty: {test.get('difficulty', 'medium')}{Colors.NC}")
        print(f"\n{Colors.YELLOW}Description:{Colors.NC}")
        print(f"  {test.get('description', 'No description provided')}")
        print(f"\n{Colors.GREEN}TASK FOR AGENT:{Colors.NC}")
        print(f"{Colors.BOLD}{test.get('prompt', 'No prompt provided')}{Colors.NC}")

        if test.get('context_files'):
            print(f"\n{Colors.BLUE}Context Files:{Colors.NC}")
            for file in test['context_files']:
                print(f"  - {file}")

        if test.get('expected_behavior'):
            print(f"\n{Colors.MAGENTA}Expected Behavior:{Colors.NC}")
            for behavior in test['expected_behavior']:
                print(f"  • {behavior}")

        print(f"{Colors.CYAN}{'='*80}{Colors.NC}\n")

    def wait_for_agent_completion(self) -> str:
        """Wait for user to confirm agent has completed task"""
        print(f"{Colors.YELLOW}Please ask the agent to perform the above task.{Colors.NC}")
        input(f"{Colors.GREEN}Press [Enter] when the agent has responded...{Colors.NC}")

        # Get user's assessment of agent response
        print("\nPlease provide the agent's response summary (or file path if saved):")
        response = input("> ").strip()
        return response

    def evaluate_test_interactive(self, test: Dict[str, Any], agent_response: str) -> Dict[str, Any]:
        """Evaluate test results with human assessment"""
        print(f"\n{Colors.CYAN}Evaluation:{Colors.NC}")

        # Show evaluation criteria if available
        domain = test.get('domain', 'unknown')
        if domain in self.evaluation_criteria:
            criteria = self.evaluation_criteria[domain]
            print(f"\n{Colors.BLUE}Evaluation Criteria:{Colors.NC}")
            for criterion in criteria.get('criteria', []):
                print(f"  • {criterion}")

        # Get human assessment
        print(f"\n{Colors.YELLOW}How did the agent perform?{Colors.NC}")
        print("1. PASS - Completed successfully")
        print("2. PARTIAL - Partially completed or had minor issues")
        print("3. FAIL - Did not complete or major issues")
        print("4. REFUSED - Agent refused the task")
        print("5. ERROR - Agent encountered errors")
        print("6. SKIP - Skip this test")

        while True:
            choice = input(f"\n{Colors.GREEN}Select option (1-6): {Colors.NC}").strip()
            status_map = {
                "1": TestStatus.PASS,
                "2": TestStatus.PARTIAL,
                "3": TestStatus.FAIL,
                "4": TestStatus.REFUSED,
                "5": TestStatus.ERROR,
                "6": TestStatus.SKIPPED
            }

            if choice in status_map:
                status = status_map[choice]
                break
            else:
                print(f"{Colors.RED}Invalid choice. Please select 1-6.{Colors.NC}")

        # Get optional notes
        notes = input(f"\n{Colors.CYAN}Additional notes (optional): {Colors.NC}").strip()

        result = {
            "test_id": test.get('id'),
            "domain": test.get('domain'),
            "status": status.value,
            "agent_response": agent_response,
            "notes": notes,
            "timestamp": datetime.now().isoformat(),
            "evaluation_mode": "interactive"
        }

        return result

    def evaluate_test_automated(self, test: Dict[str, Any], agent_response: str) -> Dict[str, Any]:
        """Evaluate test results programmatically"""
        status = TestStatus.FAIL  # Default to fail
        score = 0.0
        validation_results = {}

        # Get validation rules from test
        validations = test.get('validation', {})

        # File existence checks
        if 'files_exist' in validations:
            files_exist = validations['files_exist']
            for file_path in files_exist:
                full_path = self.base_dir / file_path
                exists = full_path.exists()
                validation_results[f"file_exists_{file_path}"] = exists
                if exists:
                    score += 1

        # Content checks
        if 'contains' in validations:
            for item in validations['contains']:
                file_path = item.get('file')
                pattern = item.get('pattern')
                if file_path and pattern:
                    full_path = self.base_dir / file_path
                    if full_path.exists():
                        with open(full_path, 'r') as f:
                            content = f.read()
                            match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE)
                            validation_results[f"contains_{pattern}"] = match is not None
                            if match:
                                score += 1

        # Response pattern checks
        if 'response_patterns' in validations:
            for pattern in validations['response_patterns']:
                match = re.search(pattern, agent_response, re.IGNORECASE | re.MULTILINE)
                validation_results[f"response_pattern_{pattern}"] = match is not None
                if match:
                    score += 1

        # Refusal detection
        refusal_keywords = ['cannot', 'unable to', 'refuse', "won't", "can't", 'inappropriate', 'against']
        is_refusal = any(keyword in agent_response.lower() for keyword in refusal_keywords)
        if is_refusal and test.get('expect_refusal', False):
            status = TestStatus.PASS
            score = 1.0
        elif is_refusal:
            status = TestStatus.REFUSED

        # Calculate final status based on score
        total_validations = len(validation_results)
        if total_validations > 0:
            pass_rate = score / total_validations
            if pass_rate >= 0.9:
                status = TestStatus.PASS
            elif pass_rate >= 0.5:
                status = TestStatus.PARTIAL
            else:
                status = TestStatus.FAIL

        result = {
            "test_id": test.get('id'),
            "domain": test.get('domain'),
            "status": status.value,
            "score": score,
            "total_validations": total_validations,
            "validation_results": validation_results,
            "agent_response": agent_response,
            "timestamp": datetime.now().isoformat(),
            "evaluation_mode": "automated"
        }

        return result

    def run_test(self, test: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single test"""
        self.current_test = test

        # Display test prompt
        self.display_test_prompt(test)

        # Wait for agent completion and get response
        agent_response = self.wait_for_agent_completion()

        # Evaluate based on mode
        if self.mode == TestMode.INTERACTIVE:
            result = self.evaluate_test_interactive(test, agent_response)
        elif self.mode == TestMode.AUTOMATED:
            result = self.evaluate_test_automated(test, agent_response)
        else:  # HYBRID
            # First try automated
            auto_result = self.evaluate_test_automated(test, agent_response)
            print(f"\n{Colors.CYAN}Automated evaluation: {auto_result['status']}{Colors.NC}")

            # Allow human override
            override = input(f"{Colors.YELLOW}Override? (y/n): {Colors.NC}").strip().lower()
            if override == 'y':
                result = self.evaluate_test_interactive(test, agent_response)
            else:
                result = auto_result

        # Update counters
        self.session_metadata['total_tests'] += 1
        status = result['status']
        if status == 'pass':
            self.session_metadata['pass_count'] += 1
        elif status == 'fail':
            self.session_metadata['fail_count'] += 1
        elif status == 'partial':
            self.session_metadata['partial_count'] += 1
        elif status == 'refused':
            self.session_metadata['refused_count'] += 1
        elif status == 'error':
            self.session_metadata['error_count'] += 1
        elif status == 'skipped':
            self.session_metadata['skipped_count'] += 1

        return result

    def run_test_suite(self, scenarios: List[Dict[str, Any]]):
        """Run all tests in the suite"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}Starting Test Suite{Colors.NC}")
        print(f"Mode: {self.mode.value}")
        print(f"Total scenarios: {len(scenarios)}\n")

        for i, test in enumerate(scenarios, 1):
            print(f"\n{Colors.BOLD}[{i}/{len(scenarios)}]{Colors.NC}")

            try:
                result = self.run_test(test)
                self.test_results.append(result)

                # Display result
                status = result['status']
                color = {
                    'pass': Colors.GREEN,
                    'partial': Colors.YELLOW,
                    'fail': Colors.RED,
                    'refused': Colors.MAGENTA,
                    'error': Colors.RED,
                    'skipped': Colors.CYAN
                }.get(status, Colors.NC)

                print(f"\n{color}Result: {status.upper()}{Colors.NC}")

            except KeyboardInterrupt:
                print(f"\n{Colors.YELLOW}Test suite interrupted by user{Colors.NC}")
                break
            except Exception as e:
                print(f"{Colors.RED}Error running test: {e}{Colors.NC}")
                continue

        # Update session metadata
        self.session_metadata['end_time'] = datetime.now().isoformat()

    def save_results(self, filename: Optional[str] = None):
        """Save test results to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_results_{timestamp}.json"

        output_path = self.results_dir / filename

        output_data = {
            "metadata": self.session_metadata,
            "results": self.test_results
        }

        with open(output_path, 'w') as f:
            json.dump(output_data, f, indent=2)

        print(f"\n{Colors.GREEN}Results saved to: {output_path}{Colors.NC}")
        return output_path

    def display_summary(self):
        """Display test summary"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.NC}")
        print(f"{Colors.BOLD}TEST SUITE SUMMARY{Colors.NC}")
        print(f"{Colors.CYAN}{'='*80}{Colors.NC}\n")

        meta = self.session_metadata
        print(f"Total Tests: {meta['total_tests']}")
        print(f"{Colors.GREEN}✓ Passed: {meta['pass_count']}{Colors.NC}")
        print(f"{Colors.YELLOW}~ Partial: {meta['partial_count']}{Colors.NC}")
        print(f"{Colors.RED}✗ Failed: {meta['fail_count']}{Colors.NC}")
        print(f"{Colors.MAGENTA}⊘ Refused: {meta['refused_count']}{Colors.NC}")
        print(f"{Colors.RED}! Errors: {meta['error_count']}{Colors.NC}")
        print(f"{Colors.CYAN}- Skipped: {meta['skipped_count']}{Colors.NC}")

        # Calculate success rate
        total_attempted = meta['total_tests'] - meta['skipped_count']
        if total_attempted > 0:
            success_rate = (meta['pass_count'] + meta['partial_count'] * 0.5) / total_attempted * 100
            print(f"\n{Colors.BOLD}Success Rate: {success_rate:.1f}%{Colors.NC}")

        # Domain breakdown
        if self.test_results:
            print(f"\n{Colors.BOLD}Results by Domain:{Colors.NC}")
            domain_stats = {}
            for result in self.test_results:
                domain = result.get('domain', 'unknown')
                if domain not in domain_stats:
                    domain_stats[domain] = {'pass': 0, 'partial': 0, 'fail': 0, 'refused': 0, 'total': 0}

                domain_stats[domain]['total'] += 1
                status = result['status']
                if status in domain_stats[domain]:
                    domain_stats[domain][status] += 1

            for domain, stats in sorted(domain_stats.items()):
                print(f"  {domain}: {stats['pass']}/{stats['total']} pass, {stats['refused']} refused")

        print(f"\n{Colors.CYAN}{'='*80}{Colors.NC}\n")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Agentic CLI Non-Coding Capability Tester",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--mode',
        type=str,
        choices=['interactive', 'automated', 'hybrid'],
        default='interactive',
        help='Test execution mode (default: interactive)'
    )

    parser.add_argument(
        '--domain',
        type=str,
        help='Filter tests by domain (e.g., research, analysis, planning)'
    )

    parser.add_argument(
        '--list-domains',
        action='store_true',
        help='List available test domains'
    )

    parser.add_argument(
        '--agent-name',
        type=str,
        default='unknown',
        help='Name of the agent being tested'
    )

    parser.add_argument(
        '--output',
        type=str,
        help='Output filename for results (default: auto-generated)'
    )

    parser.add_argument(
        '--compare',
        nargs='+',
        help='Compare results from multiple test runs'
    )

    args = parser.parse_args()

    # Handle comparison mode
    if args.compare:
        print("Comparison mode not yet implemented")
        return

    # Create tester instance
    mode = TestMode(args.mode)
    tester = AgentTester(mode=mode)
    tester.session_metadata['agent_name'] = args.agent_name

    # Load evaluation criteria
    tester.load_evaluation_criteria()

    # Load test scenarios
    scenarios = tester.load_test_scenarios(domain=args.domain)

    if not scenarios:
        print(f"{Colors.RED}No test scenarios found. Please create scenario files in test_scenarios/{Colors.NC}")
        sys.exit(1)

    # List domains if requested
    if args.list_domains:
        domains = set(s.get('domain', 'unknown') for s in scenarios)
        print(f"\n{Colors.BOLD}Available domains:{Colors.NC}")
        for domain in sorted(domains):
            count = sum(1 for s in scenarios if s.get('domain') == domain)
            print(f"  - {domain} ({count} tests)")
        print()
        return

    # Run test suite
    tester.run_test_suite(scenarios)

    # Display summary
    tester.display_summary()

    # Save results
    tester.save_results(filename=args.output)


if __name__ == "__main__":
    main()
