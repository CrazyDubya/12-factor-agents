#!/usr/bin/env python3
"""
Code Review Report Generator
Main script to generate comprehensive code review reports
"""

import argparse
import sys
from pathlib import Path
from code_analyzer import CodeAnalyzer
from report_generator import ReportGenerator


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Generate comprehensive code review reports for repositories'
    )
    parser.add_argument(
        'repository_path',
        nargs='?',
        default='.',
        help='Path to repository to analyze (default: current directory)'
    )
    parser.add_argument(
        '-o', '--output',
        default='CODE_REVIEW_REPORT.md',
        help='Output file path (default: CODE_REVIEW_REPORT.md)'
    )
    parser.add_argument(
        '-b', '--branch',
        default='main',
        help='Branch name to include in report (default: main)'
    )
    parser.add_argument(
        '-n', '--name',
        help='Repository name (default: derived from directory name)'
    )
    parser.add_argument(
        '--exclude',
        nargs='*',
        default=[],
        help='Additional directories to exclude from analysis'
    )
    
    args = parser.parse_args()
    
    # Validate repository path
    repo_path = Path(args.repository_path).resolve()
    if not repo_path.exists():
        print(f"Error: Repository path does not exist: {repo_path}", file=sys.stderr)
        sys.exit(1)
    
    if not repo_path.is_dir():
        print(f"Error: Repository path is not a directory: {repo_path}", file=sys.stderr)
        sys.exit(1)
    
    # Determine repository name
    repo_name = args.name or repo_path.name
    
    print(f"🔍 Analyzing repository: {repo_name}")
    print(f"   Path: {repo_path}")
    print(f"   Branch: {args.branch}")
    print()
    
    # Initialize analyzer with custom exclusions
    default_exclusions = {
        '.git', '__pycache__', 'node_modules', '.venv', 'venv',
        '.pytest_cache', '.mypy_cache', 'dist', 'build', '.cache',
        '.egg-info', 'htmlcov', '.tox', '.coverage', 'eggs',
        'lib', 'lib64', 'parts', 'sdist', 'var', 'wheels',
        '*.egg-info', '.installed.cfg', '*.egg'
    }
    exclusions = default_exclusions.union(set(args.exclude))
    
    analyzer = CodeAnalyzer(str(repo_path), exclude_dirs=exclusions)
    
    # Analyze repository
    print("📊 Analyzing code structure...")
    metrics = analyzer.analyze_repository()
    
    print(f"   ✓ Analyzed {metrics['code_files']} code files")
    print(f"   ✓ Found {metrics['total_classes']} classes")
    print(f"   ✓ Found {metrics['total_functions']} functions")
    print(f"   ✓ Total lines: {metrics['total_lines']:,}")
    print()
    
    # Generate report
    print("📝 Generating comprehensive report...")
    generator = ReportGenerator(repo_name, args.branch)
    report = generator.generate_full_report(metrics)
    
    # Write report to file
    output_path = Path(args.output)
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"   ✓ Report written to: {output_path.resolve()}")
    except Exception as e:
        print(f"Error writing report: {e}", file=sys.stderr)
        sys.exit(1)
    
    print()
    print("✅ Code review report generated successfully!")
    print()
    
    # Print summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total Files:      {metrics['total_files']:>8,}")
    print(f"Code Files:       {metrics['code_files']:>8,}")
    print(f"Total Lines:      {metrics['total_lines']:>8,}")
    print(f"Classes:          {metrics['total_classes']:>8,}")
    print(f"Functions:        {metrics['total_functions']:>8,}")
    print(f"TODO Items:       {metrics['total_todos']:>8,}")
    print(f"FIXME Items:      {metrics['total_fixmes']:>8,}")
    print("=" * 60)


if __name__ == '__main__':
    main()
