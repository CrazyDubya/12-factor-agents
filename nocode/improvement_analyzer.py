#!/usr/bin/env python3
"""
Agent Improvement Analyzer

Analyzes test results and generates specific recommendations for improving
agent performance, including A/B testing suggestions for prompting techniques.
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any

class ImprovementAnalyzer:
    """Analyze test results and generate improvement recommendations"""

    def __init__(self, result_files: List[Path]):
        self.result_files = result_files
        self.all_data = []
        self.load_results()

    def load_results(self):
        """Load all result files"""
        for file_path in self.result_files:
            with open(file_path, 'r') as f:
                data = json.load(f)
                self.all_data.append({
                    'file': file_path.name,
                    'metadata': data.get('metadata', {}),
                    'results': data.get('results', [])
                })

    def analyze_failure_patterns(self) -> Dict[str, Any]:
        """Identify common failure patterns across all tests"""
        patterns = {
            'missing_reasoning': [],
            'wrong_answers': [],
            'incomplete_analysis': [],
            'poor_structure': [],
            'verbose_responses': [],
            'missing_key_terms': []
        }

        for data in self.all_data:
            for result in data['results']:
                if result['status'] in ['fail', 'partial']:
                    validation = result.get('validation_details', {})

                    # Check what went wrong
                    if 'pattern_logic' in str(validation) and '✗' in str(validation.get('pattern_logic', '')):
                        patterns['missing_reasoning'].append(result)

                    if any('✗' in str(v) for k, v in validation.items() if 'pattern_' in k):
                        patterns['missing_key_terms'].append(result)

                    if validation.get('quality_appropriate_length') == '✗':
                        if result.get('full_response_length', 0) > 2000:
                            patterns['verbose_responses'].append(result)

                    if validation.get('quality_has_structure') == '✗':
                        patterns['poor_structure'].append(result)

        return patterns

    def generate_cot_recommendations(self, patterns: Dict[str, Any]) -> str:
        """Generate Chain-of-Thought prompting recommendations"""
        report = "\n" + "="*80 + "\n"
        report += "CHAIN-OF-THOUGHT (CoT) PROMPTING RECOMMENDATIONS\n"
        report += "="*80 + "\n\n"

        report += "**What is Chain-of-Thought Prompting?**\n"
        report += "CoT encourages the model to show its reasoning steps before answering,\n"
        report += "improving accuracy on complex reasoning tasks.\n\n"

        # Identify which test types would benefit
        reasoning_failures = len(patterns['missing_reasoning'])
        wrong_answers = len(patterns['wrong_answers'])

        if reasoning_failures > 0 or wrong_answers > 0:
            report += "**🎯 HIGH PRIORITY: CoT Could Help Here**\n\n"

            if reasoning_failures > 0:
                report += f"Found {reasoning_failures} tests with missing/weak reasoning.\n"
                report += "These would likely benefit from CoT prompting.\n\n"

                report += "**Example CoT Prompt Modification:**\n"
                report += "❌ BEFORE: 'Can we conclude that Sarah is a manager?'\n"
                report += "✅ AFTER:  'Can we conclude that Sarah is a manager? Think step-by-step:\n"
                report += "           1) What do we know for certain?\n"
                report += "           2) What logical rules apply?\n"
                report += "           3) What can we validly conclude?'\n\n"

            if wrong_answers > 0:
                report += f"Found {wrong_answers} tests with incorrect final answers.\n"
                report += "CoT can reduce errors by making reasoning explicit.\n\n"

                report += "**Example CoT for Math/Logic:**\n"
                report += "❌ BEFORE: 'What comes next: 2, 6, 12, 20, 30, ?'\n"
                report += "✅ AFTER:  'What comes next: 2, 6, 12, 20, 30, ?\n"
                report += "           Let's solve this step by step:\n"
                report += "           1) Find the differences between consecutive numbers\n"
                report += "           2) Identify the pattern in those differences\n"
                report += "           3) Apply the pattern to find the next number'\n\n"

        else:
            report += "**✓ LOWER PRIORITY: CoT Not Critical**\n"
            report += "Current test failures aren't primarily reasoning-related.\n"
            report += "Focus on other improvement areas first.\n\n"

        # A/B testing framework
        report += "**A/B TESTING FRAMEWORK FOR CoT**\n\n"
        report += "Recommended experiment design:\n\n"

        report += "**Branch A (Control): Standard Prompts**\n"
        report += "  - Use prompts exactly as written in test scenarios\n"
        report += "  - No additional reasoning instructions\n"
        report += "  - Baseline performance measurement\n\n"

        report += "**Branch B (Treatment): CoT-Enhanced Prompts**\n"
        report += "  - Add 'Let's think step-by-step' prefix\n"
        report += "  - Include reasoning structure hints\n"
        report += "  - Request explicit intermediate steps\n\n"

        report += "**Metrics to Compare:**\n"
        report += "  1. Overall success rate (pass + partial*0.5)\n"
        report += "  2. Reasoning domain performance specifically\n"
        report += "  3. Answer accuracy (correct final answers)\n"
        report += "  4. Response length (CoT typically longer)\n"
        report += "  5. Time to generate (CoT may be slower)\n\n"

        report += "**When to Use Each Branch:**\n"
        report += "  - Use Branch A for: Simple factual queries, communication tasks\n"
        report += "  - Use Branch B for: Complex reasoning, math, multi-step logic\n\n"

        return report

    def generate_prompt_engineering_recommendations(self, patterns: Dict[str, Any]) -> str:
        """Generate recommendations for prompt engineering improvements"""
        report = "\n" + "="*80 + "\n"
        report += "PROMPT ENGINEERING RECOMMENDATIONS\n"
        report += "="*80 + "\n\n"

        recommendations = []

        # Structure improvements
        if len(patterns['poor_structure']) > 0:
            recommendations.append({
                'issue': 'Poor Response Structure',
                'count': len(patterns['poor_structure']),
                'fix': 'Add explicit format instructions',
                'example': 'Include: "Format your answer with: 1) Overview, 2) Details, 3) Conclusion"'
            })

        # Verbosity issues
        if len(patterns['verbose_responses']) > 0:
            recommendations.append({
                'issue': 'Overly Verbose Responses',
                'count': len(patterns['verbose_responses']),
                'fix': 'Add length constraints',
                'example': 'Include: "Keep your answer concise, under 300 words"'
            })

        # Missing key information
        if len(patterns['missing_key_terms']) > 0:
            recommendations.append({
                'issue': 'Missing Required Information',
                'count': len(patterns['missing_key_terms']),
                'fix': 'Use explicit checklists',
                'example': 'Include: "Your answer must address: [list specific points]"'
            })

        for i, rec in enumerate(recommendations, 1):
            report += f"**{i}. {rec['issue']}**\n"
            report += f"   Found in {rec['count']} tests\n"
            report += f"   Fix: {rec['fix']}\n"
            report += f"   Example: {rec['example']}\n\n"

        return report

    def generate_few_shot_recommendations(self) -> str:
        """Generate few-shot learning recommendations"""
        report = "\n" + "="*80 + "\n"
        report += "FEW-SHOT LEARNING RECOMMENDATIONS\n"
        report += "="*80 + "\n\n"

        report += "**What is Few-Shot Learning?**\n"
        report += "Providing example question-answer pairs before the actual task,\n"
        report += "helping the model understand the expected format and approach.\n\n"

        report += "**A/B Test: Few-Shot vs Zero-Shot**\n\n"

        report += "**Branch A (Zero-Shot): Direct Question**\n"
        report += "  Example: 'Explain REST API to a non-technical person'\n\n"

        report += "**Branch B (Few-Shot): With Examples**\n"
        report += "  Example:\n"
        report += "  'Here are examples of technical concepts explained simply:\n"
        report += "   Q: Explain a database to a non-technical person.\n"
        report += "   A: A database is like a digital filing cabinet that stores\n"
        report += "      and organizes information so you can find it quickly.\n\n"
        report += "   Q: Explain cloud computing to a non-technical person.\n"
        report += "   A: Cloud computing is like renting storage space and computers\n"
        report += "      on the internet instead of buying your own.\n\n"
        report += "   Now you try:\n"
        report += "   Q: Explain REST API to a non-technical person.'\n\n"

        report += "**When Few-Shot Helps Most:**\n"
        report += "  - Complex formatting requirements\n"
        report += "  - Specific tone/style needed\n"
        report += "  - Unfamiliar task types\n"
        report += "  - Consistency across multiple similar queries\n\n"

        return report

    def generate_temperature_tuning_recommendations(self) -> str:
        """Generate temperature parameter recommendations"""
        report = "\n" + "="*80 + "\n"
        report += "TEMPERATURE TUNING RECOMMENDATIONS\n"
        report += "="*80 + "\n\n"

        report += "**What is Temperature?**\n"
        report += "Controls randomness in model outputs:\n"
        report += "  - Low (0.0-0.3): Deterministic, focused, consistent\n"
        report += "  - Medium (0.4-0.7): Balanced creativity and coherence\n"
        report += "  - High (0.8-1.0): Creative, diverse, exploratory\n\n"

        report += "**A/B Test: Temperature Variants**\n\n"

        report += "**Branch A: Low Temperature (0.2)**\n"
        report += "  Best for:\n"
        report += "    - Factual questions\n"
        report += "    - Logical reasoning\n"
        report += "    - Math problems\n"
        report += "    - Tasks requiring consistency\n"
        report += "  Example: 'What is 2+2?' should always return 4\n\n"

        report += "**Branch B: Medium Temperature (0.7)**\n"
        report += "  Best for:\n"
        report += "    - Creative writing\n"
        report += "    - Brainstorming\n"
        report += "    - Open-ended questions\n"
        report += "    - Varied perspectives\n"
        report += "  Example: 'Write a product tagline' benefits from variety\n\n"

        report += "**Branch C: High Temperature (1.0)**\n"
        report += "  Best for:\n"
        report += "    - Creative fiction\n"
        report += "    - Ideation sessions\n"
        report += "    - Exploring alternatives\n"
        report += "  Risk: May produce less coherent outputs\n\n"

        report += "**Recommended Test Matrix:**\n"
        report += "  Reasoning tasks → Test 0.1, 0.3, 0.5\n"
        report += "  Content creation → Test 0.5, 0.7, 0.9\n"
        report += "  Communication → Test 0.3, 0.5, 0.7\n\n"

        return report

    def generate_domain_specific_recommendations(self) -> str:
        """Generate domain-specific improvement strategies"""
        report = "\n" + "="*80 + "\n"
        report += "DOMAIN-SPECIFIC IMPROVEMENT STRATEGIES\n"
        report += "="*80 + "\n\n"

        # Analyze by domain
        domain_performance = defaultdict(lambda: {'pass': 0, 'total': 0, 'failures': []})

        for data in self.all_data:
            for result in data['results']:
                domain = result['domain']
                domain_performance[domain]['total'] += 1
                if result['status'] == 'pass':
                    domain_performance[domain]['pass'] += 1
                elif result['status'] in ['fail', 'partial']:
                    domain_performance[domain]['failures'].append(result['test_id'])

        for domain, stats in sorted(domain_performance.items()):
            rate = stats['pass'] / stats['total'] * 100 if stats['total'] > 0 else 0

            report += f"**{domain.upper()} Domain ({rate:.0f}% success)**\n\n"

            if domain == 'reasoning':
                report += "Improvement Strategies:\n"
                report += "  ✓ Implement Chain-of-Thought prompting\n"
                report += "  ✓ Use lower temperature (0.2-0.4) for consistency\n"
                report += "  ✓ Add 'Think step-by-step' instructions\n"
                report += "  ✓ Request validation of each reasoning step\n"
                report += "  ✓ Ask for confidence levels on conclusions\n\n"

            elif domain == 'communication':
                report += "Improvement Strategies:\n"
                report += "  ✓ Provide audience specification clearly\n"
                report += "  ✓ Include format examples (few-shot)\n"
                report += "  ✓ Set explicit length limits\n"
                report += "  ✓ Request specific tone (professional, casual, etc.)\n"
                report += "  ✓ Medium temperature (0.5-0.7) for balance\n\n"

            elif domain == 'content':
                report += "Improvement Strategies:\n"
                report += "  ✓ Provide style guides and examples\n"
                report += "  ✓ Use few-shot with high-quality samples\n"
                report += "  ✓ Higher temperature (0.7-0.9) for creativity\n"
                report += "  ✓ Iterate with refinement prompts\n"
                report += "  ✓ Request multiple alternatives\n\n"

            elif domain == 'refusals':
                report += "Expected Behavior:\n"
                report += "  ✓ Appropriate refusals are GOOD\n"
                report += "  ✓ Should refuse unethical/unsafe requests\n"
                report += "  ✓ Should explain why refusing\n"
                report += "  ✓ Should suggest safe alternatives\n"
                report += "  ! If refusing appropriate requests, adjust system prompt\n\n"

            if stats['failures']:
                report += f"  Failed tests: {', '.join(stats['failures'][:3])}\n"
                if len(stats['failures']) > 3:
                    report += f"  ... and {len(stats['failures']) - 3} more\n"
                report += "\n"

        return report

    def generate_ab_test_implementation_guide(self) -> str:
        """Generate implementation guide for A/B testing"""
        report = "\n" + "="*80 + "\n"
        report += "A/B TESTING IMPLEMENTATION GUIDE\n"
        report += "="*80 + "\n\n"

        report += "**Step 1: Define Test Variants**\n\n"
        report += "Create separate test runs for each variant:\n\n"

        report += "Variant A (Baseline):\n"
        report += "  - Standard prompts\n"
        report += "  - Temperature: 0.7\n"
        report += "  - No special instructions\n"
        report += "  - Command: python3 comprehensive_auto_test.py qwen2.5:3b\n\n"

        report += "Variant B (CoT):\n"
        report += "  - Add 'Think step-by-step' to all prompts\n"
        report += "  - Temperature: 0.5 (slightly lower for reasoning)\n"
        report += "  - Request explicit reasoning steps\n"
        report += "  - Command: python3 comprehensive_auto_test.py qwen2.5:3b --cot\n\n"

        report += "Variant C (Few-Shot):\n"
        report += "  - Include 2-3 examples before each query\n"
        report += "  - Temperature: 0.7\n"
        report += "  - Match examples to task type\n"
        report += "  - Command: python3 comprehensive_auto_test.py qwen2.5:3b --few-shot\n\n"

        report += "**Step 2: Run Tests**\n\n"
        report += "For statistical significance, run each variant:\n"
        report += "  - Same test scenarios\n"
        report += "  - Same model\n"
        report += "  - Same evaluation criteria\n"
        report += "  - Minimum 20+ tests per variant\n\n"

        report += "**Step 3: Analyze Results**\n\n"
        report += "Compare variants on:\n"
        report += "  Primary Metric: Success rate (pass + partial*0.5)\n"
        report += "  Secondary Metrics:\n"
        report += "    - Reasoning accuracy\n"
        report += "    - Response quality scores\n"
        report += "    - Domain-specific performance\n"
        report += "    - Response time/length\n\n"

        report += "**Step 4: Statistical Validation**\n\n"
        report += "Calculate:\n"
        report += "  - Absolute improvement: Variant B rate - Variant A rate\n"
        report += "  - Relative improvement: (B - A) / A * 100%\n"
        report += "  - Confidence: Need >5 percentage point improvement\n\n"

        report += "Example Decision Tree:\n"
        report += "  IF CoT improves reasoning by >10%:\n"
        report += "    ✓ Use CoT for reasoning tasks\n"
        report += "    ✗ Keep standard for other domains\n"
        report += "  IF Few-Shot improves communication by >15%:\n"
        report += "    ✓ Implement few-shot for content/communication\n\n"

        report += "**Step 5: Implementation**\n\n"
        report += "Create domain-specific routing:\n"
        report += "  - Reasoning tasks → Use CoT variant\n"
        report += "  - Content tasks → Use Few-Shot variant\n"
        report += "  - Simple queries → Use Baseline variant\n\n"

        return report

    def generate_full_report(self) -> str:
        """Generate comprehensive improvement report"""
        patterns = self.analyze_failure_patterns()

        report = "=" * 80 + "\n"
        report += "COMPREHENSIVE AGENT IMPROVEMENT REPORT\n"
        report += "=" * 80 + "\n"
        report += f"\nAnalyzing {len(self.all_data)} test run(s)\n"

        total_tests = sum(data['metadata'].get('total_tests', 0) for data in self.all_data)
        avg_success = sum(data['metadata'].get('success_rate', 0) for data in self.all_data) / len(self.all_data) if self.all_data else 0

        report += f"Total tests analyzed: {total_tests}\n"
        report += f"Average success rate: {avg_success:.1f}%\n"

        # Main recommendations sections
        report += self.generate_cot_recommendations(patterns)
        report += self.generate_prompt_engineering_recommendations(patterns)
        report += self.generate_few_shot_recommendations()
        report += self.generate_temperature_tuning_recommendations()
        report += self.generate_domain_specific_recommendations()
        report += self.generate_ab_test_implementation_guide()

        # Summary
        report += "\n" + "="*80 + "\n"
        report += "PRIORITY ACTION ITEMS\n"
        report += "="*80 + "\n\n"

        report += "**Immediate (This Week):**\n"
        report += "  1. Implement CoT for reasoning tasks (est. +10-20% accuracy)\n"
        report += "  2. Add explicit format instructions to reduce structure issues\n"
        report += "  3. Test temperature 0.3 for logical tasks, 0.7 for creative\n\n"

        report += "**Short-term (This Month):**\n"
        report += "  4. Build few-shot examples library for common task types\n"
        report += "  5. Run A/B tests on top 3 failing test categories\n"
        report += "  6. Create domain-specific prompt templates\n\n"

        report += "**Long-term (This Quarter):**\n"
        report += "  7. Develop automated prompt optimization pipeline\n"
        report += "  8. Build confidence calibration for uncertain answers\n"
        report += "  9. Create human-in-loop validation for critical tasks\n\n"

        report += "="*80 + "\n"
        report += "END OF IMPROVEMENT REPORT\n"
        report += "="*80 + "\n"

        return report

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 improvement_analyzer.py test_results/result1.json [result2.json ...]")
        sys.exit(1)

    result_files = [Path(f) for f in sys.argv[1:]]

    # Validate files
    valid_files = [f for f in result_files if f.exists()]
    if not valid_files:
        print("Error: No valid result files found")
        sys.exit(1)

    analyzer = ImprovementAnalyzer(valid_files)
    report = analyzer.generate_full_report()

    print(report)

    # Save to file
    output_file = Path("test_results") / f"improvement_report_{Path(sys.argv[1]).stem}.txt"
    with open(output_file, 'w') as f:
        f.write(report)

    print(f"\nReport saved to: {output_file}")

if __name__ == "__main__":
    main()
