#!/usr/bin/env python3
"""
Generate detailed explanatory analysis from test results
"""

import json
import sys
from pathlib import Path

def analyze_test_result(result: dict) -> str:
    """Generate detailed explanation for a single test result"""
    test_id = result['test_id']
    domain = result['domain']
    status = result['status']
    score = result.get('score', 0)
    max_score = result.get('max_score', 0)
    response = result['agent_response']
    validation = result.get('validation_details', {})

    explanation = f"\n{'='*80}\n"
    explanation += f"TEST: {test_id} ({domain})\n"
    explanation += f"{'='*80}\n\n"

    # Overall assessment
    status_explanations = {
        'pass': "✓ PASSED - The agent successfully completed this task.",
        'partial': "~ PARTIAL - The agent completed some aspects but missed others.",
        'fail': "✗ FAILED - The agent did not successfully complete this task.",
        'refused': "⊘ REFUSED - The agent appropriately declined this request."
    }

    explanation += f"**Result:** {status_explanations.get(status, status.upper())}\n\n"

    if max_score > 0:
        explanation += f"**Score:** {score}/{max_score} ({score/max_score*100:.0f}%)\n\n"

    # Explain what was checked
    explanation += "**What Was Tested:**\n"

    # Parse validation details
    patterns_found = []
    patterns_missing = []
    quality_passed = []
    quality_failed = []

    for key, value in validation.items():
        if key.startswith('pattern_'):
            pattern_text = key.replace('pattern_', '').replace('|', ' OR ')
            if '✓' in value:
                patterns_found.append(pattern_text)
            else:
                patterns_missing.append(pattern_text)
        elif key.startswith('quality_'):
            quality_name = key.replace('quality_', '').replace('_', ' ').title()
            if '✓' in value:
                quality_passed.append(quality_name)
            else:
                quality_failed.append(quality_name)

    # Explain pattern matching
    if patterns_found:
        explanation += "\n✓ **Found Expected Elements:**\n"
        for i, pattern in enumerate(patterns_found, 1):
            explanation += f"  {i}. Response included: {pattern}\n"
            explanation += f"     WHY THIS MATTERS: Shows the agent understood and addressed this aspect.\n"

    if patterns_missing:
        explanation += "\n✗ **Missing Expected Elements:**\n"
        for i, pattern in enumerate(patterns_missing, 1):
            explanation += f"  {i}. Response should have included: {pattern}\n"
            explanation += f"     WHY THIS MATTERS: Critical information was omitted or incorrect.\n"

    # Explain quality
    if quality_passed or quality_failed:
        explanation += "\n**Response Quality:**\n"
        for quality in quality_passed:
            explanation += f"  ✓ {quality}\n"
        for quality in quality_failed:
            explanation += f"  ✗ {quality}\n"

    # Show response excerpt
    explanation += f"\n**Agent's Response (first 300 chars):**\n"
    explanation += f'"{response[:300]}..."\n'

    # Provide specific feedback
    explanation += "\n**Analysis:**\n"

    if status == 'pass':
        explanation += "The agent demonstrated competence in this task. "
        if score == max_score:
            explanation += "It met all validation criteria with accurate, complete information."
        else:
            explanation += f"It met {score}/{max_score} criteria, showing solid understanding with room for improvement."

    elif status == 'partial':
        explanation += f"The agent showed partial understanding, meeting {score}/{max_score} criteria. "
        if patterns_missing:
            explanation += f"Key missing elements: {', '.join(patterns_missing[:2])}. "
        explanation += "This suggests the agent grasped the core concept but lacked completeness or precision."

    elif status == 'fail':
        explanation += "The agent struggled with this task. "
        if patterns_missing:
            explanation += f"Failed to include essential elements like: {', '.join(patterns_missing[:2])}. "
        explanation += "This indicates a gap in capability for this type of request."

    explanation += "\n"

    return explanation

def generate_domain_insights(results: list) -> str:
    """Generate insights by domain"""
    insights = "\n" + "="*80 + "\n"
    insights += "DOMAIN PERFORMANCE INSIGHTS\n"
    insights += "="*80 + "\n\n"

    # Group by domain
    by_domain = {}
    for result in results:
        domain = result['domain']
        if domain not in by_domain:
            by_domain[domain] = []
        by_domain[domain].append(result)

    for domain, domain_results in sorted(by_domain.items()):
        passed = sum(1 for r in domain_results if r['status'] == 'pass')
        total = len(domain_results)
        rate = passed / total * 100 if total > 0 else 0

        insights += f"**{domain.upper()} Domain:** {passed}/{total} passed ({rate:.0f}%)\n\n"

        if rate >= 75:
            insights += f"✓ STRENGTH: The agent performs well in {domain} tasks.\n"
            insights += f"  - Successfully handled {passed} out of {total} scenarios\n"
            insights += f"  - Demonstrates reliable competence in this area\n"

        elif rate >= 50:
            insights += f"~ MODERATE: The agent has mixed results in {domain} tasks.\n"
            insights += f"  - {passed} passes suggest capability exists\n"
            insights += f"  - {total - passed} failures indicate inconsistency\n"
            insights += f"  - May need additional prompting or context for reliability\n"

        else:
            insights += f"✗ WEAKNESS: The agent struggles with {domain} tasks.\n"
            insights += f"  - Only {passed}/{total} successful completions\n"
            insights += f"  - Consider using alternative agents for {domain} work\n"

        # Specific examples
        best = max(domain_results, key=lambda x: x.get('score', 0))
        worst = min(domain_results, key=lambda x: x.get('score', 0))

        insights += f"\n  Best Performance: {best['test_id']} ({best.get('score', 0)}/{best.get('max_score', 1)} score)\n"
        insights += f"  Needs Work: {worst['test_id']} ({worst.get('score', 0)}/{worst.get('max_score', 1)} score)\n\n"

    return insights

def generate_recommendations(results: list, metadata: dict) -> str:
    """Generate actionable recommendations"""
    recs = "\n" + "="*80 + "\n"
    recs += "ACTIONABLE RECOMMENDATIONS\n"
    recs += "="*80 + "\n\n"

    agent_name = metadata.get('agent_name', 'This agent')
    success_rate = metadata.get('success_rate', 0)

    recs += f"**Overall Assessment for {agent_name}:**\n\n"

    if success_rate >= 80:
        recs += f"✓ RECOMMENDED FOR GENERAL USE ({success_rate:.0f}% success rate)\n\n"
        recs += "This agent demonstrates strong capabilities across tested domains.\n"
        recs += "Suitable for production use with standard monitoring.\n\n"

        recs += "**Best Use Cases:**\n"
        # Find strongest domains
        by_domain = {}
        for r in results:
            domain = r['domain']
            if domain not in by_domain:
                by_domain[domain] = {'pass': 0, 'total': 0}
            by_domain[domain]['total'] += 1
            if r['status'] == 'pass':
                by_domain[domain]['pass'] += 1

        top_domains = sorted(by_domain.items(), key=lambda x: x[1]['pass'] / x[1]['total'] if x[1]['total'] > 0 else 0, reverse=True)[:2]
        for domain, stats in top_domains:
            rate = stats['pass'] / stats['total'] * 100 if stats['total'] > 0 else 0
            recs += f"  - {domain.capitalize()} tasks ({rate:.0f}% success)\n"

    elif success_rate >= 60:
        recs += f"~ USE WITH CAUTION ({success_rate:.0f}% success rate)\n\n"
        recs += "This agent shows capability but with notable gaps.\n"
        recs += "Recommend human review of outputs, especially for critical tasks.\n\n"

        recs += "**Recommended Approach:**\n"
        recs += "  - Use for non-critical tasks first\n"
        recs += "  - Implement validation workflows\n"
        recs += "  - Consider fallback options for important work\n\n"

    else:
        recs += f"✗ NOT RECOMMENDED FOR PRODUCTION ({success_rate:.0f}% success rate)\n\n"
        recs += "This agent shows significant limitations in tested scenarios.\n"
        recs += "Consider alternative agents or additional training/prompting.\n\n"

    # Specific improvements
    weak_areas = []
    by_domain = {}
    for r in results:
        domain = r['domain']
        if domain not in by_domain:
            by_domain[domain] = []
        by_domain[domain].append(r['status'])

    for domain, statuses in by_domain.items():
        pass_rate = sum(1 for s in statuses if s == 'pass') / len(statuses) * 100
        if pass_rate < 60:
            weak_areas.append(f"{domain} ({pass_rate:.0f}%)")

    if weak_areas:
        recs += "**Areas Needing Improvement:**\n"
        for area in weak_areas:
            recs += f"  - {area}\n"
        recs += "\n"

    return recs

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 analyze_results.py test_results/your_results.json")
        sys.exit(1)

    result_file = Path(sys.argv[1])
    if not result_file.exists():
        print(f"Error: File not found: {result_file}")
        sys.exit(1)

    with open(result_file, 'r') as f:
        data = json.load(f)

    metadata = data.get('metadata', {})
    results = data.get('results', [])

    print("="*80)
    print("DETAILED EXPLANATORY ANALYSIS")
    print("="*80)
    print(f"\nAgent: {metadata.get('agent_name', 'Unknown')}")
    print(f"Tests Run: {metadata.get('total_tests', 0)}")
    print(f"Overall Success: {metadata.get('success_rate', 0):.1f}%")
    print()

    # Individual test explanations
    for result in results[:5]:  # First 5 for brevity
        print(analyze_test_result(result))

    if len(results) > 5:
        print(f"\n... and {len(results) - 5} more tests (use full report for all)\n")

    # Domain insights
    print(generate_domain_insights(results))

    # Recommendations
    print(generate_recommendations(results, metadata))

    print("="*80)
    print("END OF ANALYSIS")
    print("="*80)

if __name__ == "__main__":
    main()
