#!/usr/bin/env python3
"""
Multi-Agent Comparison Tool

Compares test results from multiple agents and generates comparative analysis.

Usage:
    python compare_agents.py test_results/test_results_*.json
    python compare_agents.py --agents copilot qwen llama
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
from collections import defaultdict


class AgentComparator:
    """Compare multiple agent test results"""

    def __init__(self, result_files: List[Path]):
        self.result_files = result_files
        self.agents_data = []
        self.load_all_results()

    def load_all_results(self):
        """Load all result files"""
        for file_path in self.result_files:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    self.agents_data.append({
                        'file': file_path.name,
                        'metadata': data.get('metadata', {}),
                        'results': data.get('results', [])
                    })
                    print(f"✓ Loaded: {file_path.name}")
            except Exception as e:
                print(f"✗ Error loading {file_path}: {e}")

        print(f"\nLoaded {len(self.agents_data)} agent result files\n")

    def calculate_statistics(self) -> Dict[str, Dict[str, Any]]:
        """Calculate statistics for each agent"""
        stats = {}

        for agent in self.agents_data:
            meta = agent['metadata']
            results = agent['results']
            agent_name = meta.get('agent_name', 'Unknown')

            # Overall stats
            total = meta.get('total_tests', 0)
            passed = meta.get('pass_count', 0)
            partial = meta.get('partial_count', 0)
            failed = meta.get('fail_count', 0)
            refused = meta.get('refused_count', 0)

            success_rate = 0
            if total > 0:
                success_rate = ((passed + partial * 0.5) / total) * 100

            # Domain breakdown
            domain_stats = defaultdict(lambda: {'pass': 0, 'partial': 0, 'fail': 0, 'refused': 0, 'total': 0})

            for result in results:
                domain = result.get('domain', 'unknown')
                status = result.get('status', 'unknown')

                domain_stats[domain]['total'] += 1
                if status in ['pass', 'partial', 'fail', 'refused']:
                    domain_stats[domain][status] += 1

            # Calculate domain success rates
            domain_success_rates = {}
            for domain, counts in domain_stats.items():
                total_domain = counts['total']
                if total_domain > 0:
                    rate = ((counts['pass'] + counts['partial'] * 0.5) / total_domain) * 100
                    domain_success_rates[domain] = rate
                else:
                    domain_success_rates[domain] = 0

            stats[agent_name] = {
                'total_tests': total,
                'passed': passed,
                'partial': partial,
                'failed': failed,
                'refused': refused,
                'success_rate': success_rate,
                'domain_stats': dict(domain_stats),
                'domain_success_rates': domain_success_rates,
                'mode': meta.get('mode', 'unknown')
            }

        return stats

    def generate_comparison_html(self, stats: Dict[str, Dict[str, Any]]) -> str:
        """Generate HTML comparison report"""
        # Get all unique domains
        all_domains = set()
        for agent_stats in stats.values():
            all_domains.update(agent_stats['domain_stats'].keys())
        all_domains = sorted(all_domains)

        # Generate agent comparison table
        agent_rows = ""
        for agent_name, agent_stats in sorted(stats.items()):
            success_rate = agent_stats['success_rate']
            color = self._get_color_for_rate(success_rate)

            agent_rows += f"""
            <tr>
                <td><strong>{agent_name}</strong></td>
                <td>{agent_stats['total_tests']}</td>
                <td style="color: #10b981;">{agent_stats['passed']}</td>
                <td style="color: #f59e0b;">{agent_stats['partial']}</td>
                <td style="color: #ef4444;">{agent_stats['failed']}</td>
                <td style="color: #6366f1;">{agent_stats['refused']}</td>
                <td style="background: {color}; font-weight: bold;">{success_rate:.1f}%</td>
            </tr>
            """

        # Generate domain comparison matrix
        domain_rows = ""
        for domain in all_domains:
            domain_rows += f"<tr><td><strong>{domain.title()}</strong></td>"

            for agent_name in sorted(stats.keys()):
                rate = stats[agent_name]['domain_success_rates'].get(domain, 0)
                tests = stats[agent_name]['domain_stats'].get(domain, {}).get('total', 0)
                color = self._get_color_for_rate(rate)

                if tests > 0:
                    domain_rows += f'<td style="background: {color}; font-weight: bold;">{rate:.0f}%<br><small>({tests} tests)</small></td>'
                else:
                    domain_rows += '<td style="background: #f3f4f6; color: #9ca3af;">N/A</td>'

            domain_rows += "</tr>"

        # Get agent names for headers
        agent_headers = "".join([f"<th>{name}</th>" for name in sorted(stats.keys())])

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agent Comparison Report</title>
    <style>
        {self._get_styles()}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔬 Multi-Agent Comparison Report</h1>
            <p class="meta">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p class="meta">Agents Compared: {len(stats)}</p>
        </div>

        <div class="section">
            <h2>📊 Overall Performance Comparison</h2>
            <table class="comparison-table">
                <thead>
                    <tr>
                        <th>Agent</th>
                        <th>Total Tests</th>
                        <th>Passed</th>
                        <th>Partial</th>
                        <th>Failed</th>
                        <th>Refused</th>
                        <th>Success Rate</th>
                    </tr>
                </thead>
                <tbody>
                    {agent_rows}
                </tbody>
            </table>
        </div>

        <div class="section">
            <h2>🎯 Domain Performance Matrix</h2>
            <p class="subtitle">Success rate by domain for each agent</p>
            <div class="table-wrapper">
                <table class="matrix-table">
                    <thead>
                        <tr>
                            <th>Domain</th>
                            {agent_headers}
                        </tr>
                    </thead>
                    <tbody>
                        {domain_rows}
                    </tbody>
                </table>
            </div>
        </div>

        {self._generate_insights_section(stats)}

        <div class="footer">
            <p>Generated by Agent Comparison Tool v1.0</p>
        </div>
    </div>
</body>
</html>
"""
        return html

    def _generate_insights_section(self, stats: Dict[str, Dict[str, Any]]) -> str:
        """Generate insights and recommendations"""
        # Find best overall performer
        best_agent = max(stats.items(), key=lambda x: x[1]['success_rate'])
        best_name = best_agent[0]
        best_rate = best_agent[1]['success_rate']

        # Find best per domain
        all_domains = set()
        for agent_stats in stats.values():
            all_domains.update(agent_stats['domain_stats'].keys())

        domain_leaders = {}
        for domain in all_domains:
            leader = max(
                stats.items(),
                key=lambda x: x[1]['domain_success_rates'].get(domain, 0)
            )
            domain_leaders[domain] = {
                'agent': leader[0],
                'rate': leader[1]['domain_success_rates'].get(domain, 0)
            }

        # Generate insights HTML
        domain_insights = ""
        for domain, leader_info in sorted(domain_leaders.items()):
            domain_insights += f"""
            <div class="insight-item">
                <strong>{domain.title()}</strong>: {leader_info['agent']} ({leader_info['rate']:.0f}%)
            </div>
            """

        return f"""
        <div class="section">
            <h2>💡 Key Insights</h2>

            <div class="insight-box">
                <h3>🏆 Overall Winner</h3>
                <p><strong>{best_name}</strong> achieved the highest overall success rate of <strong>{best_rate:.1f}%</strong></p>
            </div>

            <div class="insight-box">
                <h3>🎯 Domain Leaders</h3>
                {domain_insights}
            </div>

            <div class="insight-box">
                <h3>📋 Recommendations</h3>
                <div class="insight-item">
                    <strong>Best Overall:</strong> Use {best_name} for general-purpose tasks
                </div>
                <div class="insight-item">
                    <strong>Tool Operations:</strong> Agents with file/web capabilities excel at research and analysis
                </div>
                <div class="insight-item">
                    <strong>Text Tasks:</strong> Text-only models perform well on reasoning, content, and communication
                </div>
            </div>
        </div>
        """

    def _get_color_for_rate(self, rate: float) -> str:
        """Get color based on success rate"""
        if rate >= 90:
            return '#10b981'  # Green
        elif rate >= 75:
            return '#84cc16'  # Lime
        elif rate >= 60:
            return '#eab308'  # Yellow
        elif rate >= 45:
            return '#f97316'  # Orange
        else:
            return '#ef4444'  # Red

    def _get_styles(self) -> str:
        """CSS styles for comparison report"""
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #1f2937;
            background: #f9fafb;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }

        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }

        .meta {
            opacity: 0.9;
            font-size: 1.1em;
        }

        .section {
            background: white;
            padding: 30px;
            margin-bottom: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .section h2 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.8em;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }

        .subtitle {
            color: #6b7280;
            margin-bottom: 20px;
        }

        .comparison-table,
        .matrix-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }

        .comparison-table th,
        .comparison-table td,
        .matrix-table th,
        .matrix-table td {
            padding: 12px;
            text-align: center;
            border: 1px solid #e5e7eb;
        }

        .comparison-table th,
        .matrix-table th {
            background: #667eea;
            color: white;
            font-weight: bold;
        }

        .comparison-table tbody tr:hover,
        .matrix-table tbody tr:hover {
            background: #f3f4f6;
        }

        .table-wrapper {
            overflow-x: auto;
        }

        .insight-box {
            background: linear-gradient(135deg, #f0f9ff 0%, #e0e7ff 100%);
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            border-left: 4px solid #667eea;
        }

        .insight-box h3 {
            color: #667eea;
            margin-bottom: 15px;
        }

        .insight-item {
            padding: 10px 0;
            border-bottom: 1px solid #e5e7eb;
        }

        .insight-item:last-child {
            border-bottom: none;
        }

        .footer {
            text-align: center;
            padding: 20px;
            color: #6b7280;
        }

        @media print {
            body { background: white; }
            .section { box-shadow: none; }
        }
        """

    def save_comparison_report(self, output_path: Path):
        """Generate and save comparison report"""
        print("Calculating statistics...")
        stats = self.calculate_statistics()

        print("Generating HTML report...")
        html = self.generate_comparison_html(stats)

        with open(output_path, 'w') as f:
            f.write(html)

        print(f"\n✓ Comparison report saved to: {output_path}")

        # Print summary to console
        print(f"\n{'='*80}")
        print("AGENT COMPARISON SUMMARY")
        print(f"{'='*80}\n")

        for agent_name, agent_stats in sorted(stats.items()):
            print(f"{agent_name}:")
            print(f"  Success Rate: {agent_stats['success_rate']:.1f}%")
            print(f"  Tests: {agent_stats['total_tests']} total, "
                  f"{agent_stats['passed']} passed, "
                  f"{agent_stats['partial']} partial, "
                  f"{agent_stats['failed']} failed")
            print()

        print(f"{'='*80}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Compare multiple agent test results"
    )

    parser.add_argument(
        'result_files',
        nargs='+',
        type=Path,
        help='JSON result files to compare'
    )

    parser.add_argument(
        '--output',
        type=Path,
        help='Output filename for comparison report'
    )

    args = parser.parse_args()

    # Validate files exist
    valid_files = []
    for file_path in args.result_files:
        if file_path.exists():
            valid_files.append(file_path)
        else:
            print(f"Warning: File not found: {file_path}")

    if len(valid_files) < 2:
        print("Error: Need at least 2 result files to compare")
        sys.exit(1)

    # Determine output path
    if args.output:
        output_path = args.output
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = Path("test_results") / f"comparison_report_{timestamp}.html"

    # Create comparator and generate report
    comparator = AgentComparator(valid_files)
    comparator.save_comparison_report(output_path)


if __name__ == "__main__":
    main()
