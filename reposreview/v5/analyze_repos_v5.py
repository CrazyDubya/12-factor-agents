#!/usr/bin/env python3
"""
v5 Repository Analyzer - Powered by Expanded Models (128K Context)

Re-analyzes all repositories using expanded models:
- qwen-128k for large repos (100+ files)
- llama3-32k for medium repos (50-100 files)
- gemma2-32k for quality analysis
- mistral-32k for documentation generation

Uses 128K context windows to analyze entire repositories at once.
"""

import json
import requests
import time
from datetime import datetime
from pathlib import Path

OLLAMA_URL = "http://localhost:11434"

class ExpandedModelAnalyzer:
    def __init__(self):
        self.results = []
        self.stats = {
            'total': 0,
            'analyzed': 0,
            'failed': 0,
            'models_used': {},
            'total_tokens': 0,
            'total_time': 0
        }

    def select_model(self, repo):
        """Select optimal expanded model based on repository size"""
        # Estimate size from language data
        total_bytes = sum(repo.get('languages', {}).values())
        file_count = len(repo.get('topics', [])) + 10  # Rough estimate

        if total_bytes > 500000 or file_count > 100:
            return 'qwen-128k', '128K'
        elif total_bytes > 100000 or file_count > 50:
            return 'llama3-32k', '32K'
        else:
            return 'gemma2-32k', '32K'

    def analyze_repository(self, repo):
        """Deep analysis using expanded models"""
        print(f"\n{'='*80}")
        print(f"Analyzing: {repo['name']}")
        print(f"{'='*80}")

        model, context = self.select_model(repo)
        print(f"Selected model: {model} ({context} context)")

        # Build comprehensive prompt with all repo data
        prompt = self.build_analysis_prompt(repo)

        start_time = time.time()

        try:
            # Call Ollama with expanded model
            response = requests.post(
                f"{OLLAMA_URL}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": 8192,  # Allow detailed output
                        "temperature": 0.6,
                        "top_p": 0.85
                    }
                },
                timeout=300  # 5 min timeout for large repos
            )

            if response.status_code == 200:
                result = response.json()
                elapsed = time.time() - start_time
                tokens = len(result['response']) // 4  # Rough estimate

                print(f"✓ Analysis complete in {elapsed:.1f}s ({tokens} tokens)")

                # Update stats
                self.stats['analyzed'] += 1
                self.stats['models_used'][model] = self.stats['models_used'].get(model, 0) + 1
                self.stats['total_tokens'] += tokens
                self.stats['total_time'] += elapsed

                # Parse AI response into structured data
                analysis = self.parse_analysis(result['response'])

                return {
                    **repo,
                    'v5_analysis': {
                        'model_used': model,
                        'context_window': context,
                        'analysis_time': elapsed,
                        'tokens_generated': tokens,
                        'timestamp': datetime.now().isoformat(),
                        'architecture': analysis.get('architecture'),
                        'security': analysis.get('security'),
                        'quality_deep': analysis.get('quality'),
                        'recommendations': analysis.get('recommendations'),
                        'comprehensive_summary': result['response'][:500] + '...',
                        'full_analysis': result['response']
                    }
                }
            else:
                print(f"✗ Error: {response.status_code}")
                self.stats['failed'] += 1
                return None

        except Exception as e:
            print(f"✗ Failed: {str(e)}")
            self.stats['failed'] += 1
            return None

    def build_analysis_prompt(self, repo):
        """Build comprehensive analysis prompt"""
        return f"""Analyze this GitHub repository in detail:

Repository: {repo['name']}
Description: {repo.get('description', 'No description')}
Language: {repo.get('language', 'Unknown')}
Stars: {repo.get('stargazers_count', 0)}
Forks: {repo.get('forks_count', 0)}
Open Issues: {repo.get('open_issues_count', 0)}

Languages Used:
{json.dumps(repo.get('languages', {}), indent=2)}

Topics: {', '.join(repo.get('topics', []))}

Previous Analysis:
{json.dumps(repo.get('ai_analysis', {}), indent=2)}

Provide a COMPREHENSIVE analysis covering:

1. ARCHITECTURE ANALYSIS
   - Overall design and structure
   - Component organization
   - Design patterns used
   - Scalability considerations

2. SECURITY ASSESSMENT
   - Potential vulnerabilities
   - Security best practices
   - Authentication/authorization approach
   - Data protection measures

3. CODE QUALITY EVALUATION
   - Code organization and clarity
   - Documentation completeness
   - Testing coverage
   - Maintainability score

4. TECHNOLOGY STACK ANALYSIS
   - Primary technologies and their usage
   - Dependencies and their quality
   - Modern best practices adoption
   - Technical debt assessment

5. RECOMMENDATIONS
   - Specific improvements needed
   - Priority actions
   - Best practices to implement
   - Future enhancement suggestions

Provide detailed, actionable insights using the entire context window available to you.
"""

    def parse_analysis(self, response):
        """Extract structured data from AI response"""
        # Simple parsing - can be enhanced with more sophisticated extraction
        sections = {
            'architecture': '',
            'security': '',
            'quality': '',
            'recommendations': []
        }

        current_section = None
        lines = response.split('\n')

        for line in lines:
            line_lower = line.lower()
            if 'architecture' in line_lower and ':' in line:
                current_section = 'architecture'
            elif 'security' in line_lower and ':' in line:
                current_section = 'security'
            elif 'quality' in line_lower and ':' in line:
                current_section = 'quality'
            elif 'recommendation' in line_lower and ':' in line:
                current_section = 'recommendations'
            elif current_section and line.strip():
                if current_section == 'recommendations':
                    if line.strip().startswith('-') or line.strip().startswith('•'):
                        sections[current_section].append(line.strip()[1:].strip())
                else:
                    sections[current_section] += line + '\n'

        return sections

    def run_full_analysis(self, input_file='crazydubya_repositories_aiml_deep.json',
                         limit=None, skip=0):
        """Run analysis on all repositories"""
        print(f"\n{'='*80}")
        print("V5 REPOSITORY ANALYZER - EXPANDED MODELS (128K CONTEXT)")
        print(f"{'='*80}\n")

        # Load existing data
        print(f"Loading repositories from {input_file}...")
        with open(input_file, 'r') as f:
            data = json.load(f)

        repos = data['repositories']
        self.stats['total'] = len(repos)

        if limit:
            repos = repos[skip:skip+limit]
            print(f"Processing {len(repos)} repositories (skip={skip}, limit={limit})")
        else:
            repos = repos[skip:]
            print(f"Processing {len(repos)} repositories (starting from {skip})")

        print(f"\nStarting analysis...")
        print(f"Models available: qwen-128k, llama3-32k, gemma2-32k\n")

        # Analyze each repository
        for i, repo in enumerate(repos, 1):
            print(f"\nProgress: {i}/{len(repos)}")

            result = self.analyze_repository(repo)
            if result:
                self.results.append(result)

            # Progress checkpoint every 10 repos
            if i % 10 == 0:
                self.save_checkpoint(i)

        # Save final results
        self.save_results()
        self.print_summary()

    def save_checkpoint(self, count):
        """Save checkpoint"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        checkpoint_file = f"v5/data/checkpoint_{count}_{timestamp}.json"

        with open(checkpoint_file, 'w') as f:
            json.dump({
                'repositories': self.results,
                'stats': self.stats,
                'checkpoint': count
            }, f, indent=2)

        print(f"\n✓ Checkpoint saved: {checkpoint_file}")

    def save_results(self):
        """Save final results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"crazydubya_repositories_v5_expanded_{timestamp}.json"

        output = {
            'version': '5.0',
            'analysis_engine': 'Expanded Models (128K Context)',
            'models_used': list(self.stats['models_used'].keys()),
            'timestamp': datetime.now().isoformat(),
            'stats': self.stats,
            'repositories': self.results
        }

        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2)

        print(f"\n✓ Results saved: {output_file}")
        return output_file

    def print_summary(self):
        """Print analysis summary"""
        print(f"\n{'='*80}")
        print("ANALYSIS COMPLETE")
        print(f"{'='*80}\n")

        print(f"Total repositories: {self.stats['total']}")
        print(f"Successfully analyzed: {self.stats['analyzed']}")
        print(f"Failed: {self.stats['failed']}")
        print(f"\nModels used:")
        for model, count in self.stats['models_used'].items():
            print(f"  {model}: {count} repos")

        print(f"\nTotal tokens generated: {self.stats['total_tokens']:,}")
        print(f"Total analysis time: {self.stats['total_time']:.1f}s")

        if self.stats['analyzed'] > 0:
            avg_time = self.stats['total_time'] / self.stats['analyzed']
            avg_tokens = self.stats['total_tokens'] / self.stats['analyzed']
            print(f"Average per repo: {avg_time:.1f}s, {avg_tokens:.0f} tokens")

def main():
    import sys

    analyzer = ExpandedModelAnalyzer()

    # Parse command line args
    limit = None
    skip = 0

    if len(sys.argv) > 1:
        if '--limit' in sys.argv:
            idx = sys.argv.index('--limit')
            limit = int(sys.argv[idx + 1])
        if '--skip' in sys.argv:
            idx = sys.argv.index('--skip')
            skip = int(sys.argv[idx + 1])

    # Run analysis
    analyzer.run_full_analysis(limit=limit, skip=skip)

if __name__ == '__main__':
    main()
