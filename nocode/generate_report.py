#!/usr/bin/env python3
"""
HTML Report Generator for Agent Test Results

Generates interactive HTML reports with visualizations from test result JSON files.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any


class ReportGenerator:
    """Generate HTML reports from test results"""

    def __init__(self, results_file: Path):
        self.results_file = results_file
        with open(results_file, 'r') as f:
            self.data = json.load(f)

        self.metadata = self.data.get('metadata', {})
        self.results = self.data.get('results', [])

    def generate_html(self) -> str:
        """Generate complete HTML report"""
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agent Test Report - {self.metadata.get('agent_name', 'Unknown')}</title>
    <style>
        {self._get_styles()}
    </style>
</head>
<body>
    <div class="container">
        {self._generate_header()}
        {self._generate_summary()}
        {self._generate_domain_breakdown()}
        {self._generate_capability_matrix()}
        {self._generate_refusals_section()}
        {self._generate_detailed_results()}
        {self._generate_footer()}
    </div>
    <script>
        {self._get_scripts()}
    </script>
</body>
</html>
"""
        return html

    def _get_styles(self) -> str:
        """CSS styles for the report"""
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }

        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }

        .header .meta {
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

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }

        .stat-card {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }

        .stat-card.pass { background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%); }
        .stat-card.partial { background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); }
        .stat-card.fail { background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%); }
        .stat-card.refused { background: linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%); }

        .stat-number {
            font-size: 3em;
            font-weight: bold;
            color: #333;
        }

        .stat-label {
            font-size: 1em;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .domain-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }

        .domain-card {
            border: 2px solid #e0e0e0;
            padding: 20px;
            border-radius: 8px;
            transition: all 0.3s ease;
        }

        .domain-card:hover {
            border-color: #667eea;
            box-shadow: 0 4px 8px rgba(102, 126, 234, 0.2);
        }

        .domain-card h3 {
            color: #667eea;
            margin-bottom: 10px;
        }

        .domain-stats {
            display: flex;
            justify-content: space-between;
            margin-top: 15px;
        }

        .domain-stat {
            text-align: center;
        }

        .domain-stat-value {
            font-size: 1.5em;
            font-weight: bold;
        }

        .domain-stat-label {
            font-size: 0.8em;
            color: #666;
        }

        .progress-bar {
            width: 100%;
            height: 10px;
            background: #e0e0e0;
            border-radius: 5px;
            overflow: hidden;
            margin-top: 10px;
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            transition: width 0.3s ease;
        }

        .capability-matrix {
            overflow-x: auto;
        }

        .matrix-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }

        .matrix-table th,
        .matrix-table td {
            padding: 12px;
            text-align: center;
            border: 1px solid #e0e0e0;
        }

        .matrix-table th {
            background: #667eea;
            color: white;
            font-weight: bold;
        }

        .matrix-cell {
            font-weight: bold;
            font-size: 1.2em;
        }

        .matrix-cell.excellent { background: #84fab0; color: #1a1a1a; }
        .matrix-cell.good { background: #ffecd2; color: #1a1a1a; }
        .matrix-cell.poor { background: #ff9a9e; color: #1a1a1a; }
        .matrix-cell.none { background: #f5f5f5; color: #999; }

        .test-result {
            border-left: 4px solid #e0e0e0;
            padding: 15px;
            margin-bottom: 15px;
            background: #f9f9f9;
            border-radius: 4px;
        }

        .test-result.pass { border-left-color: #84fab0; }
        .test-result.partial { border-left-color: #fcb69f; }
        .test-result.fail { border-left-color: #ff9a9e; }
        .test-result.refused { border-left-color: #a1c4fd; }
        .test-result.error { border-left-color: #ff6b6b; }

        .test-result-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }

        .test-id {
            font-weight: bold;
            color: #667eea;
        }

        .test-status {
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: bold;
            text-transform: uppercase;
        }

        .test-status.pass { background: #84fab0; color: #1a1a1a; }
        .test-status.partial { background: #fcb69f; color: #1a1a1a; }
        .test-status.fail { background: #ff9a9e; color: #1a1a1a; }
        .test-status.refused { background: #a1c4fd; color: #1a1a1a; }
        .test-status.error { background: #ff6b6b; color: white; }

        .test-notes {
            margin-top: 10px;
            padding: 10px;
            background: white;
            border-radius: 4px;
            font-style: italic;
            color: #666;
        }

        .footer {
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 0.9em;
        }

        .refusal-item {
            background: #f0f4ff;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 4px;
            border-left: 4px solid #667eea;
        }

        .refusal-item h4 {
            color: #667eea;
            margin-bottom: 5px;
        }

        @media print {
            body { background: white; }
            .section { box-shadow: none; }
        }
        """

    def _generate_header(self) -> str:
        """Generate report header"""
        agent_name = self.metadata.get('agent_name', 'Unknown Agent')
        start_time = self.metadata.get('start_time', 'Unknown')
        mode = self.metadata.get('mode', 'Unknown')

        return f"""
        <div class="header">
            <h1>🤖 Agent Test Report</h1>
            <div class="meta">
                <p><strong>Agent:</strong> {agent_name}</p>
                <p><strong>Test Date:</strong> {start_time}</p>
                <p><strong>Mode:</strong> {mode}</p>
            </div>
        </div>
        """

    def _generate_summary(self) -> str:
        """Generate summary statistics"""
        meta = self.metadata
        total = meta.get('total_tests', 0)
        passed = meta.get('pass_count', 0)
        partial = meta.get('partial_count', 0)
        failed = meta.get('fail_count', 0)
        refused = meta.get('refused_count', 0)

        success_rate = 0
        if total > 0:
            success_rate = ((passed + partial * 0.5) / total) * 100

        return f"""
        <div class="section">
            <h2>📊 Summary</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{total}</div>
                    <div class="stat-label">Total Tests</div>
                </div>
                <div class="stat-card pass">
                    <div class="stat-number">{passed}</div>
                    <div class="stat-label">Passed</div>
                </div>
                <div class="stat-card partial">
                    <div class="stat-number">{partial}</div>
                    <div class="stat-label">Partial</div>
                </div>
                <div class="stat-card fail">
                    <div class="stat-number">{failed}</div>
                    <div class="stat-label">Failed</div>
                </div>
                <div class="stat-card refused">
                    <div class="stat-number">{refused}</div>
                    <div class="stat-label">Refused</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{success_rate:.1f}%</div>
                    <div class="stat-label">Success Rate</div>
                </div>
            </div>
        </div>
        """

    def _generate_domain_breakdown(self) -> str:
        """Generate domain-by-domain breakdown"""
        # Calculate domain stats
        domain_stats = {}
        for result in self.results:
            domain = result.get('domain', 'unknown')
            if domain not in domain_stats:
                domain_stats[domain] = {'pass': 0, 'partial': 0, 'fail': 0, 'refused': 0, 'total': 0}

            domain_stats[domain]['total'] += 1
            status = result.get('status', 'unknown')
            if status in domain_stats[domain]:
                domain_stats[domain][status] += 1

        domain_cards = ""
        for domain, stats in sorted(domain_stats.items()):
            total = stats['total']
            passed = stats['pass']
            partial = stats['partial']
            success_rate = ((passed + partial * 0.5) / total * 100) if total > 0 else 0

            domain_cards += f"""
            <div class="domain-card">
                <h3>{domain.title()}</h3>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {success_rate}%"></div>
                </div>
                <div class="domain-stats">
                    <div class="domain-stat">
                        <div class="domain-stat-value" style="color: #84fab0;">{stats['pass']}</div>
                        <div class="domain-stat-label">Pass</div>
                    </div>
                    <div class="domain-stat">
                        <div class="domain-stat-value" style="color: #fcb69f;">{stats['partial']}</div>
                        <div class="domain-stat-label">Partial</div>
                    </div>
                    <div class="domain-stat">
                        <div class="domain-stat-value" style="color: #ff9a9e;">{stats['fail']}</div>
                        <div class="domain-stat-label">Fail</div>
                    </div>
                    <div class="domain-stat">
                        <div class="domain-stat-value" style="color: #a1c4fd;">{stats['refused']}</div>
                        <div class="domain-stat-label">Refused</div>
                    </div>
                </div>
            </div>
            """

        return f"""
        <div class="section">
            <h2>📈 Domain Breakdown</h2>
            <div class="domain-grid">
                {domain_cards}
            </div>
        </div>
        """

    def _generate_capability_matrix(self) -> str:
        """Generate capability matrix heatmap"""
        # Calculate domain performance
        domain_stats = {}
        for result in self.results:
            domain = result.get('domain', 'unknown')
            if domain not in domain_stats:
                domain_stats[domain] = []

            status = result.get('status')
            if status == 'pass':
                domain_stats[domain].append(1.0)
            elif status == 'partial':
                domain_stats[domain].append(0.5)
            elif status == 'fail':
                domain_stats[domain].append(0.0)

        matrix_rows = ""
        for domain, scores in sorted(domain_stats.items()):
            avg_score = sum(scores) / len(scores) if scores else 0
            cell_class = "excellent" if avg_score >= 0.75 else "good" if avg_score >= 0.5 else "poor"

            matrix_rows += f"""
            <tr>
                <td><strong>{domain.title()}</strong></td>
                <td class="matrix-cell {cell_class}">{avg_score:.0%}</td>
                <td>{len(scores)}</td>
            </tr>
            """

        return f"""
        <div class="section">
            <h2>🎯 Capability Matrix</h2>
            <div class="capability-matrix">
                <table class="matrix-table">
                    <thead>
                        <tr>
                            <th>Domain</th>
                            <th>Success Rate</th>
                            <th>Tests</th>
                        </tr>
                    </thead>
                    <tbody>
                        {matrix_rows}
                    </tbody>
                </table>
            </div>
        </div>
        """

    def _generate_refusals_section(self) -> str:
        """Generate section for refusals and boundaries"""
        refusals = [r for r in self.results if r.get('status') == 'refused']

        if not refusals:
            return """
            <div class="section">
                <h2>🚫 Refusals & Boundaries</h2>
                <p>No refusals recorded in this test session.</p>
            </div>
            """

        refusal_items = ""
        for r in refusals:
            refusal_items += f"""
            <div class="refusal-item">
                <h4>{r.get('test_id', 'Unknown')}</h4>
                <p><strong>Domain:</strong> {r.get('domain', 'Unknown')}</p>
                {f'<p><strong>Notes:</strong> {r.get("notes")}</p>' if r.get('notes') else ''}
            </div>
            """

        return f"""
        <div class="section">
            <h2>🚫 Refusals & Boundaries</h2>
            <p>Tests where the agent appropriately refused or encountered boundaries: <strong>{len(refusals)}</strong></p>
            {refusal_items}
        </div>
        """

    def _generate_detailed_results(self) -> str:
        """Generate detailed test results"""
        results_html = ""
        for result in self.results:
            test_id = result.get('test_id', 'Unknown')
            status = result.get('status', 'unknown')
            domain = result.get('domain', 'unknown')
            notes = result.get('notes', '')
            timestamp = result.get('timestamp', '')

            results_html += f"""
            <div class="test-result {status}">
                <div class="test-result-header">
                    <span class="test-id">{test_id}</span>
                    <span class="test-status {status}">{status}</span>
                </div>
                <p><strong>Domain:</strong> {domain}</p>
                <p><strong>Time:</strong> {timestamp}</p>
                {f'<div class="test-notes">{notes}</div>' if notes else ''}
            </div>
            """

        return f"""
        <div class="section">
            <h2>📋 Detailed Results</h2>
            {results_html}
        </div>
        """

    def _generate_footer(self) -> str:
        """Generate report footer"""
        return f"""
        <div class="footer">
            <p>Generated by Agent Tester v1.0 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        """

    def _get_scripts(self) -> str:
        """JavaScript for interactivity"""
        return """
        // Add any interactive features here
        console.log('Agent Test Report loaded');
        """

    def save_report(self, output_path: Path):
        """Save HTML report to file"""
        html = self.generate_html()
        with open(output_path, 'w') as f:
            f.write(html)
        print(f"Report saved to: {output_path}")


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python generate_report.py <results_file.json> [output.html]")
        sys.exit(1)

    results_file = Path(sys.argv[1])
    if not results_file.exists():
        print(f"Error: Results file not found: {results_file}")
        sys.exit(1)

    # Determine output path
    if len(sys.argv) >= 3:
        output_path = Path(sys.argv[2])
    else:
        output_path = results_file.parent / f"{results_file.stem}_report.html"

    # Generate report
    generator = ReportGenerator(results_file)
    generator.save_report(output_path)


if __name__ == "__main__":
    main()
