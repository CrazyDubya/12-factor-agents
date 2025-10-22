#!/usr/bin/env python3
"""
Generate ACTIONABLE report with REAL data - actual responses, patterns, comparisons
"""

import json
import sys
from pathlib import Path

def generate_real_report(results_file):
    """Generate report with actual agent responses and data"""

    with open(results_file, 'r') as f:
        data = json.load(f)

    metadata = data.get('metadata', {})
    results = data.get('results', [])

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Real Test Results - {metadata.get('agent_name')}</title>
    <style>
        body {{
            font-family: 'SF Mono', Monaco, 'Courier New', monospace;
            background: #1e1e1e;
            color: #d4d4d4;
            padding: 20px;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        h1, h2, h3 {{
            color: #4ec9b0;
            border-bottom: 2px solid #4ec9b0;
            padding-bottom: 10px;
        }}
        .summary {{
            background: #252526;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            border-left: 4px solid #4ec9b0;
        }}
        .test-block {{
            background: #252526;
            padding: 20px;
            margin: 20px 0;
            border-radius: 8px;
            border-left: 4px solid #666;
        }}
        .test-block.pass {{ border-left-color: #4ec9b0; }}
        .test-block.partial {{ border-left-color: #ce9178; }}
        .test-block.fail {{ border-left-color: #f48771; }}

        .metric {{
            display: inline-block;
            background: #1e1e1e;
            padding: 8px 15px;
            margin: 5px;
            border-radius: 4px;
            border: 1px solid #4ec9b0;
        }}
        .metric strong {{ color: #4ec9b0; }}

        .response-box {{
            background: #1e1e1e;
            padding: 15px;
            border-radius: 4px;
            margin: 10px 0;
            border: 1px solid #3e3e42;
            white-space: pre-wrap;
            font-size: 13px;
            overflow-x: auto;
        }}
        .pattern {{
            display: inline-block;
            padding: 4px 8px;
            margin: 3px;
            border-radius: 3px;
            font-size: 12px;
            font-family: monospace;
        }}
        .pattern.found {{
            background: #1a4d2e;
            color: #4ec9b0;
            border: 1px solid #4ec9b0;
        }}
        .pattern.missing {{
            background: #4d1a1a;
            color: #f48771;
            border: 1px solid #f48771;
        }}
        .char-count {{
            color: #ce9178;
            font-weight: bold;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }}
        th, td {{
            padding: 10px;
            border: 1px solid #3e3e42;
            text-align: left;
        }}
        th {{
            background: #2d2d30;
            color: #4ec9b0;
        }}
        .pass-check {{ color: #4ec9b0; }}
        .fail-check {{ color: #f48771; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 ACTUAL TEST RESULTS - REAL DATA</h1>

        <div class="summary">
            <h2>Summary</h2>
            <div class="metric"><strong>Model:</strong> {metadata.get('agent_name', 'Unknown')}</div>
            <div class="metric"><strong>Success Rate:</strong> {metadata.get('success_rate', 0):.1f}%</div>
            <div class="metric"><strong>Tests:</strong> {metadata.get('total_tests', 0)}</div>
            <div class="metric"><strong>Passed:</strong> {metadata.get('pass_count', 0)}</div>
            <div class="metric"><strong>Partial:</strong> {metadata.get('partial_count', 0)}</div>
            <div class="metric"><strong>Failed:</strong> {metadata.get('fail_count', 0)}</div>
            <div class="metric"><strong>Quality Score:</strong> {metadata.get('average_quality_score', 0):.1f}/4</div>
        </div>
"""

    # Generate detailed test results
    for idx, result in enumerate(results, 1):
        test_id = result.get('test_id', 'unknown')
        domain = result.get('domain', 'unknown')
        status = result.get('status', 'unknown')
        score = result.get('score', 0)
        max_score = result.get('max_score', 1)
        response = result.get('agent_response', 'No response')
        response_length = result.get('full_response_length', len(response))
        validation = result.get('validation_details', {})
        quality_score = result.get('quality_score', 0)

        # Pattern analysis
        patterns_found = []
        patterns_missing = []
        for key, value in validation.items():
            if key.startswith('pattern_'):
                pattern_text = key.replace('pattern_', '')
                if '✓' in value:
                    patterns_found.append(pattern_text)
                else:
                    patterns_missing.append(pattern_text)

        # Quality checks
        quality_checks = []
        for key, value in validation.items():
            if key.startswith('quality_'):
                quality_name = key.replace('quality_', '').replace('_', ' ').title()
                status_icon = '✓' if '✓' in value else '✗'
                quality_checks.append((quality_name, status_icon))

        html += f"""
        <div class="test-block {status}">
            <h2>Test #{idx}: {test_id}</h2>

            <table>
                <tr>
                    <th>Metric</th>
                    <th>Value</th>
                </tr>
                <tr>
                    <td>Domain</td>
                    <td><strong>{domain}</strong></td>
                </tr>
                <tr>
                    <td>Status</td>
                    <td><strong class="{'pass-check' if status == 'pass' else 'fail-check'}">{status.upper()}</strong></td>
                </tr>
                <tr>
                    <td>Score</td>
                    <td><strong>{score}/{max_score}</strong> ({score/max_score*100:.0f}%)</td>
                </tr>
                <tr>
                    <td>Quality Score</td>
                    <td><strong>{quality_score}/4</strong></td>
                </tr>
                <tr>
                    <td>Response Length</td>
                    <td><span class="char-count">{response_length:,} characters</span></td>
                </tr>
            </table>

            <h3>Pattern Matching</h3>
            <div>
"""

        if patterns_found:
            html += "<p><strong>✓ FOUND:</strong><br>"
            for pattern in patterns_found:
                html += f'<span class="pattern found">✓ {pattern}</span>'
            html += "</p>"

        if patterns_missing:
            html += "<p><strong>✗ MISSING:</strong><br>"
            for pattern in patterns_missing:
                html += f'<span class="pattern missing">✗ {pattern}</span>'
            html += "</p>"

        if quality_checks:
            html += "<p><strong>Quality Checks:</strong><br>"
            for check_name, check_status in quality_checks:
                color_class = 'pass-check' if check_status == '✓' else 'fail-check'
                html += f'<span class="{color_class}">{check_status} {check_name}</span> &nbsp; '
            html += "</p>"

        html += f"""
            </div>

            <h3>Actual Agent Response</h3>
            <div class="response-box">{response}</div>
        </div>
"""

    html += """
    </div>
</body>
</html>
"""

    return html

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 generate_real_report.py <results.json>")
        sys.exit(1)

    results_file = Path(sys.argv[1])
    if not results_file.exists():
        print(f"Error: {results_file} not found")
        sys.exit(1)

    html = generate_real_report(results_file)

    output_file = results_file.parent / f"{results_file.stem}_REAL_report.html"
    with open(output_file, 'w') as f:
        f.write(html)

    print(f"✓ Real report saved: {output_file}")
    print(f"  This report shows ACTUAL agent responses and data")
    return output_file

if __name__ == '__main__':
    output = main()
    import subprocess
    subprocess.run(['open', str(output)])
