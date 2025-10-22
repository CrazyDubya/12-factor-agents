#!/usr/bin/env python3
"""
Generate BEFORE/AFTER comparison report with actual agent responses
"""

import json
import sys
from pathlib import Path

def generate_comparison(before_file, after_file):
    """Generate side-by-side comparison report"""

    with open(before_file, 'r') as f:
        before_data = json.load(f)

    with open(after_file, 'r') as f:
        after_data = json.load(f)

    before_meta = before_data.get('metadata', {})
    after_meta = after_data.get('metadata', {})
    before_results = before_data.get('results', [])
    after_results = after_data.get('results', [])

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>BEFORE/AFTER Comparison - Real Data</title>
    <style>
        body {{
            font-family: 'SF Mono', Monaco, 'Courier New', monospace;
            background: #1e1e1e;
            color: #d4d4d4;
            padding: 20px;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1600px;
            margin: 0 auto;
        }}
        h1, h2, h3 {{
            color: #4ec9b0;
            border-bottom: 2px solid #4ec9b0;
            padding-bottom: 10px;
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin: 20px 0;
        }}
        .summary-box {{
            background: #252526;
            padding: 20px;
            border-radius: 8px;
        }}
        .summary-box.before {{ border-left: 4px solid #ce9178; }}
        .summary-box.after {{ border-left: 4px solid #4ec9b0; }}
        .metric {{
            margin: 10px 0;
            padding: 10px;
            background: #1e1e1e;
            border-radius: 4px;
        }}
        .metric .label {{
            color: #858585;
            font-size: 12px;
            text-transform: uppercase;
        }}
        .metric .value {{
            color: #4ec9b0;
            font-size: 24px;
            font-weight: bold;
        }}
        .improvement {{
            color: #4ec9b0;
            font-weight: bold;
        }}
        .degradation {{
            color: #f48771;
            font-weight: bold;
        }}
        .comparison-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin: 20px 0;
        }}
        .test-panel {{
            background: #252526;
            padding: 15px;
            border-radius: 8px;
        }}
        .test-panel.before {{ border-left: 4px solid #ce9178; }}
        .test-panel.after {{ border-left: 4px solid #4ec9b0; }}
        .test-panel.changed {{ border: 2px solid #dcdcaa; }}
        .response-box {{
            background: #1e1e1e;
            padding: 10px;
            border-radius: 4px;
            margin: 10px 0;
            white-space: pre-wrap;
            font-size: 12px;
            max-height: 400px;
            overflow-y: auto;
            border: 1px solid #3e3e42;
        }}
        .pattern {{
            display: inline-block;
            padding: 3px 8px;
            margin: 2px;
            border-radius: 3px;
            font-size: 11px;
        }}
        .pattern.found {{
            background: #1a4d2e;
            color: #4ec9b0;
        }}
        .pattern.missing {{
            background: #4d1a1a;
            color: #f48771;
        }}
        .char-count {{
            color: #ce9178;
            font-weight: bold;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0;
        }}
        th, td {{
            padding: 8px;
            border: 1px solid #3e3e42;
            text-align: left;
            font-size: 13px;
        }}
        th {{
            background: #2d2d30;
            color: #4ec9b0;
        }}
        .status-badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: bold;
            text-transform: uppercase;
        }}
        .status-badge.pass {{ background: #1a4d2e; color: #4ec9b0; }}
        .status-badge.partial {{ background: #4d3a1a; color: #ce9178; }}
        .status-badge.fail {{ background: #4d1a1a; color: #f48771; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 BEFORE/AFTER COMPARISON - REAL DATA</h1>

        <div class="summary-grid">
            <div class="summary-box before">
                <h2>❌ BEFORE (Original Prompts)</h2>
                <div class="metric">
                    <div class="label">Success Rate</div>
                    <div class="value">{before_meta.get('success_rate', 0):.1f}%</div>
                </div>
                <div class="metric">
                    <div class="label">Passed / Total</div>
                    <div class="value">{before_meta.get('pass_count', 0)}/{before_meta.get('total_tests', 0)}</div>
                </div>
                <div class="metric">
                    <div class="label">Partial</div>
                    <div class="value">{before_meta.get('partial_count', 0)}</div>
                </div>
                <div class="metric">
                    <div class="label">Quality Score</div>
                    <div class="value">{before_meta.get('average_quality_score', 0):.1f}/4</div>
                </div>
            </div>

            <div class="summary-box after">
                <h2>✅ AFTER (Fixed Prompts)</h2>
                <div class="metric">
                    <div class="label">Success Rate</div>
                    <div class="value">{after_meta.get('success_rate', 0):.1f}%</div>
                </div>
                <div class="metric">
                    <div class="label">Passed / Total</div>
                    <div class="value">{after_meta.get('pass_count', 0)}/{after_meta.get('total_tests', 0)}</div>
                </div>
                <div class="metric">
                    <div class="label">Partial</div>
                    <div class="value">{after_meta.get('partial_count', 0)}</div>
                </div>
                <div class="metric">
                    <div class="label">Quality Score</div>
                    <div class="value">{after_meta.get('average_quality_score', 0):.1f}/4</div>
                </div>
            </div>
        </div>

        <div class="summary-box">
            <h2>📈 IMPROVEMENT METRICS</h2>
            <table>
                <tr>
                    <th>Metric</th>
                    <th>Before</th>
                    <th>After</th>
                    <th>Change</th>
                </tr>
                <tr>
                    <td>Success Rate</td>
                    <td>{before_meta.get('success_rate', 0):.1f}%</td>
                    <td>{after_meta.get('success_rate', 0):.1f}%</td>
                    <td class="improvement">+{after_meta.get('success_rate', 0) - before_meta.get('success_rate', 0):.1f}%</td>
                </tr>
                <tr>
                    <td>Tests Passed</td>
                    <td>{before_meta.get('pass_count', 0)}</td>
                    <td>{after_meta.get('pass_count', 0)}</td>
                    <td class="improvement">+{after_meta.get('pass_count', 0) - before_meta.get('pass_count', 0)}</td>
                </tr>
                <tr>
                    <td>Partial Tests</td>
                    <td>{before_meta.get('partial_count', 0)}</td>
                    <td>{after_meta.get('partial_count', 0)}</td>
                    <td class="improvement">{after_meta.get('partial_count', 0) - before_meta.get('partial_count', 0)}</td>
                </tr>
                <tr>
                    <td>Quality Score</td>
                    <td>{before_meta.get('average_quality_score', 0):.1f}</td>
                    <td>{after_meta.get('average_quality_score', 0):.1f}</td>
                    <td class="improvement">+{after_meta.get('average_quality_score', 0) - before_meta.get('average_quality_score', 0):.1f}</td>
                </tr>
            </table>
        </div>

        <h2>🔍 TEST-BY-TEST COMPARISON</h2>
"""

    # Compare each test
    for before_result in before_results:
        test_id = before_result.get('test_id')
        after_result = next((r for r in after_results if r.get('test_id') == test_id), None)

        if not after_result:
            continue

        before_status = before_result.get('status', 'unknown')
        after_status = after_result.get('status', 'unknown')
        changed = before_status != after_status

        before_score = before_result.get('score', 0)
        before_max = before_result.get('max_score', 1)
        after_score = after_result.get('score', 0)
        after_max = after_result.get('max_score', 1)

        before_length = before_result.get('full_response_length', 0)
        after_length = after_result.get('full_response_length', 0)
        length_reduction = ((before_length - after_length) / before_length * 100) if before_length > 0 else 0

        before_response = before_result.get('agent_response', '')
        after_response = after_result.get('agent_response', '')

        before_validation = before_result.get('validation_details', {})
        after_validation = after_result.get('validation_details', {})

        html += f"""
        <div style="margin: 30px 0; padding: 20px; background: #2d2d30; border-radius: 8px; {'border: 2px solid #dcdcaa;' if changed else ''}">
            <h3>{test_id} {'⚠️ CHANGED' if changed else ''}</h3>

            <table>
                <tr>
                    <th>Metric</th>
                    <th>Before</th>
                    <th>After</th>
                    <th>Change</th>
                </tr>
                <tr>
                    <td>Status</td>
                    <td><span class="status-badge {before_status}">{before_status}</span></td>
                    <td><span class="status-badge {after_status}">{after_status}</span></td>
                    <td>{'✓ IMPROVED' if after_status == 'pass' and before_status != 'pass' else '-'}</td>
                </tr>
                <tr>
                    <td>Score</td>
                    <td>{before_score}/{before_max} ({before_score/before_max*100:.0f}%)</td>
                    <td>{after_score}/{after_max} ({after_score/after_max*100:.0f}%)</td>
                    <td class="{'improvement' if after_score > before_score else ''}">{'+' if after_score > before_score else ''}{after_score - before_score}</td>
                </tr>
                <tr>
                    <td>Response Length</td>
                    <td class="char-count">{before_length:,} chars</td>
                    <td class="char-count">{after_length:,} chars</td>
                    <td class="{'improvement' if length_reduction > 0 else ''}">{'-' if length_reduction > 0 else ''}{abs(length_reduction):.0f}%</td>
                </tr>
            </table>

            <div class="comparison-grid">
                <div class="test-panel before">
                    <h4>❌ BEFORE</h4>
                    <p><strong>Patterns:</strong></p>
"""

        # Before patterns
        for key, value in before_validation.items():
            if key.startswith('pattern_'):
                pattern = key.replace('pattern_', '')
                status = 'found' if '✓' in value else 'missing'
                icon = '✓' if status == 'found' else '✗'
                html += f'<span class="pattern {status}">{icon} {pattern}</span>'

        html += f"""
                    <h4>Response ({before_length:,} chars):</h4>
                    <div class="response-box">{before_response[:1000]}{'...' if len(before_response) > 1000 else ''}</div>
                </div>

                <div class="test-panel after">
                    <h4>✅ AFTER</h4>
                    <p><strong>Patterns:</strong></p>
"""

        # After patterns
        for key, value in after_validation.items():
            if key.startswith('pattern_'):
                pattern = key.replace('pattern_', '')
                status = 'found' if '✓' in value else 'missing'
                icon = '✓' if status == 'found' else '✗'
                html += f'<span class="pattern {status}">{icon} {pattern}</span>'

        html += f"""
                    <h4>Response ({after_length:,} chars):</h4>
                    <div class="response-box">{after_response[:1000]}{'...' if len(after_response) > 1000 else ''}</div>
                </div>
            </div>
        </div>
"""

    html += """
    </div>
</body>
</html>
"""

    return html

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 generate_comparison_report.py <before.json> <after.json>")
        sys.exit(1)

    before_file = Path(sys.argv[1])
    after_file = Path(sys.argv[2])

    if not before_file.exists() or not after_file.exists():
        print("Error: Files not found")
        sys.exit(1)

    html = generate_comparison(before_file, after_file)

    output_file = Path('test_results/BEFORE_AFTER_COMPARISON.html')
    with open(output_file, 'w') as f:
        f.write(html)

    print(f"✓ Comparison report saved: {output_file}")
    print(f"  Shows side-by-side ACTUAL agent responses and data")
    return output_file

if __name__ == '__main__':
    output = main()
    import subprocess
    subprocess.run(['open', str(output)])
