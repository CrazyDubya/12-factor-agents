#!/usr/bin/env python3
"""
Theater Critics System - Test Runner

This script provides convenient ways to run different types of tests
with appropriate configurations and reporting.
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle the output."""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print("=" * 60)

    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if result.stdout:
            print("STDOUT:")
            print(result.stdout)

        if result.stderr:
            print("STDERR:")
            print(result.stderr)

        if result.returncode != 0:
            print(f"❌ Command failed with return code {result.returncode}")
            return False
        else:
            print("✅ Command completed successfully")
            return True

    except Exception as e:
        print(f"❌ Error running command: {e}")
        return False


def run_unit_tests():
    """Run unit tests only."""
    cmd = "python -m pytest tests/ -v -m unit --tb=short"
    return run_command(cmd, "Running Unit Tests")


def run_integration_tests():
    """Run integration tests only."""
    cmd = "python -m pytest tests/ -v -m integration --tb=short"
    return run_command(cmd, "Running Integration Tests")


def run_api_tests():
    """Run API tests only."""
    cmd = "python -m pytest tests/ -v -m api --tb=short"
    return run_command(cmd, "Running API Tests")


def run_all_tests():
    """Run all tests with coverage."""
    cmd = "python -m pytest tests/ -v --cov=. --cov-report=html --cov-report=term-missing --tb=short"
    return run_command(cmd, "Running All Tests with Coverage")


def run_fast_tests():
    """Run fast tests only (exclude slow tests)."""
    cmd = "python -m pytest tests/ -v -m 'not slow' --tb=short"
    return run_command(cmd, "Running Fast Tests Only")


def run_linting():
    """Run code linting checks."""
    success = True

    # Run flake8
    success &= run_command(
        "python -m flake8 . --config=setup.cfg", "Running Flake8 Linting"
    )

    # Run pylint on main modules
    success &= run_command(
        "python -m pylint main.py --rcfile=.pylintrc", "Running Pylint on Main Module"
    )

    # Run black check
    success &= run_command(
        "python -m black --check --diff .", "Running Black Code Format Check"
    )

    # Run isort check
    success &= run_command(
        "python -m isort --check-only --diff .", "Running Import Sort Check"
    )

    return success


def run_type_checking():
    """Run mypy type checking."""
    return run_command(
        "python -m mypy main.py --config-file=pyproject.toml",
        "Running MyPy Type Checking",
    )


def run_security_check():
    """Run security analysis with bandit."""
    return run_command(
        "python -m bandit -r . -x tests/ -ll", "Running Security Analysis with Bandit"
    )


def run_quality_suite():
    """Run complete code quality suite."""
    print(f"\n{'='*80}")
    print("🏆 THEATER CRITICS SYSTEM - COMPLETE QUALITY SUITE")
    print("=" * 80)

    success = True

    # Run linting
    success &= run_linting()

    # Run type checking
    success &= run_type_checking()

    # Run security check
    success &= run_security_check()

    # Run all tests
    success &= run_all_tests()

    print(f"\n{'='*80}")
    if success:
        print("✅ ALL QUALITY CHECKS PASSED!")
    else:
        print("❌ SOME QUALITY CHECKS FAILED!")
    print("=" * 80)

    return success


def install_dependencies():
    """Install development dependencies."""
    cmd = "pip install -r requirements-dev.txt"
    return run_command(cmd, "Installing Development Dependencies")


def format_code():
    """Format code with black and isort."""
    success = True

    success &= run_command("python -m black .", "Formatting Code with Black")

    success &= run_command("python -m isort .", "Sorting Imports with isort")

    return success


def main():
    """Main entry point for test runner."""
    parser = argparse.ArgumentParser(
        description="Theater Critics System Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py --unit                 # Run unit tests only
  python run_tests.py --integration          # Run integration tests only
  python run_tests.py --api                  # Run API tests only
  python run_tests.py --all                  # Run all tests with coverage
  python run_tests.py --fast                 # Run fast tests only
  python run_tests.py --lint                 # Run linting checks
  python run_tests.py --type-check           # Run type checking
  python run_tests.py --security             # Run security analysis
  python run_tests.py --quality              # Run complete quality suite
  python run_tests.py --install-deps         # Install development dependencies
  python run_tests.py --format               # Format code
        """,
    )

    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument(
        "--integration", action="store_true", help="Run integration tests only"
    )
    parser.add_argument("--api", action="store_true", help="Run API tests only")
    parser.add_argument(
        "--all", action="store_true", help="Run all tests with coverage"
    )
    parser.add_argument("--fast", action="store_true", help="Run fast tests only")
    parser.add_argument("--lint", action="store_true", help="Run linting checks")
    parser.add_argument("--type-check", action="store_true", help="Run type checking")
    parser.add_argument("--security", action="store_true", help="Run security analysis")
    parser.add_argument(
        "--quality", action="store_true", help="Run complete quality suite"
    )
    parser.add_argument(
        "--install-deps", action="store_true", help="Install development dependencies"
    )
    parser.add_argument("--format", action="store_true", help="Format code")

    args = parser.parse_args()

    # If no specific args, run all tests
    if not any(vars(args).values()):
        args.all = True

    success = True

    if args.install_deps:
        success &= install_dependencies()

    if args.format:
        success &= format_code()

    if args.unit:
        success &= run_unit_tests()

    if args.integration:
        success &= run_integration_tests()

    if args.api:
        success &= run_api_tests()

    if args.all:
        success &= run_all_tests()

    if args.fast:
        success &= run_fast_tests()

    if args.lint:
        success &= run_linting()

    if args.type_check:
        success &= run_type_checking()

    if args.security:
        success &= run_security_check()

    if args.quality:
        success &= run_quality_suite()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
