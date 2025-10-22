# Agentic CLI Non-Coding Capability Tester

A comprehensive testing framework for evaluating AI agents on non-coding tasks including research, analysis, planning, reasoning, and boundary testing.

## 🎯 Overview

This framework tests AI agents across **8 core capability domains** with **50+ test scenarios**, focusing on tasks that don't involve writing code but are critical for general-purpose AI assistants.

### Capability Domains

1. **Research & Information Gathering** - Web search, documentation reading, fact verification
2. **Data Analysis & Interpretation** - CSV/JSON analysis, pattern recognition, insights
3. **Content Creation & Editing** - Writing, summarization, formatting, style adaptation
4. **Planning & Organization** - Task breakdown, prioritization, resource estimation
5. **Multi-Tool Coordination** - Complex workflows using multiple tools
6. **Reasoning & Problem-Solving** - Logic, inference, trade-off analysis
7. **Refusals & Boundaries** - Security, privacy, ethical boundaries
8. **Communication Quality** - Clarity, conciseness, audience adaptation

## 📁 Project Structure

```
nocode/
├── agent_tester.py              # Main test orchestrator
├── generate_report.py           # HTML report generator
├── evaluation_criteria.yaml     # Scoring rubrics
├── test_scenarios/              # Test definitions (YAML)
│   ├── research_scenarios.yaml
│   ├── analysis_scenarios.yaml
│   ├── content_scenarios.yaml
│   ├── planning_scenarios.yaml
│   ├── multitool_scenarios.yaml
│   ├── reasoning_scenarios.yaml
│   ├── refusal_scenarios.yaml
│   └── communication_scenarios.yaml
├── test_data/                   # Sample data files for tests
│   ├── sales_data.csv
│   ├── reviews.txt
│   ├── long_article.md
│   └── ... (18+ test data files)
└── test_results/                # Output directory for results
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- PyYAML library

```bash
pip install pyyaml
```

### Running Tests

**Interactive Mode** (recommended for first-time use):
```bash
python agent_tester.py --mode interactive --agent-name "Claude Code"
```

**Automated Mode** (uses validation rules):
```bash
python agent_tester.py --mode automated --agent-name "MyAgent"
```

**Hybrid Mode** (automated evaluation with human override):
```bash
python agent_tester.py --mode hybrid
```

**Domain-Specific Testing**:
```bash
python agent_tester.py --domain research
python agent_tester.py --domain analysis
```

**List Available Domains**:
```bash
python agent_tester.py --list-domains
```

### Generating Reports

After running tests, generate an HTML report:

```bash
python generate_report.py test_results/test_results_TIMESTAMP.json
```

This creates an interactive HTML dashboard with:
- Overall performance metrics
- Domain-by-domain breakdown
- Capability heatmap
- Refusal tracking
- Detailed test results

## 📊 Test Execution Modes

### Interactive Mode
- Human evaluates each test
- Ideal for subjective assessments
- Captures qualitative insights
- Allows for nuanced scoring

### Automated Mode
- Programmatic evaluation using validation rules
- Fast execution
- Consistent scoring
- Best for regression testing

### Hybrid Mode
- Automated evaluation first
- Human can override
- Balances speed with human judgment

## 🧪 Test Scenario Format

Test scenarios are defined in YAML files:

```yaml
domain: research
description: Tests for research and information gathering

tests:
  - id: research_001
    name: "Web Search - Basic Facts"
    difficulty: easy
    description: "Test ability to find and verify basic information"
    prompt: "Use web search to find who won the Nobel Prize in Literature in 2023."
    expected_behavior:
      - "Uses WebSearch tool"
      - "Provides correct answer"
      - "Cites sources"
    validation:
      response_patterns:
        - "Jon Fosse"
        - "2023"
    tags: [web-search, factual]
```

## 📈 Evaluation Criteria

Each domain has specific evaluation criteria defined in `evaluation_criteria.yaml`:

- **Excellent** (1.0): Comprehensive, accurate, well-executed
- **Good** (0.75): Solid performance with minor issues
- **Acceptable** (0.5): Basic completion with some gaps
- **Poor** (0.25): Incomplete or significant problems

## 🎨 Adding Custom Tests

1. Create or edit a YAML file in `test_scenarios/`
2. Follow the test scenario format
3. Add any required test data to `test_data/`
4. Run tests with your new scenarios

Example:
```yaml
- id: custom_001
  name: "My Custom Test"
  difficulty: medium
  description: "Description of what this tests"
  prompt: "The exact task to give the agent"
  expected_behavior:
    - "What the agent should do"
  validation:
    response_patterns:
      - "pattern to match in response"
  tags: [custom, category]
```

## 📋 Sample Test Scenarios

### Research
- Web search for facts with verification
- Documentation navigation
- Multi-source research and synthesis
- Fact checking and debunking

### Analysis
- CSV data analysis and statistics
- Pattern recognition in time series
- Multi-file data synthesis
- Text analysis and sentiment extraction

### Content
- Document summarization
- Multi-document synthesis
- Style adaptation for different audiences
- Content editing and improvement

### Planning
- Complex task breakdown
- Dependency identification
- Resource estimation
- Risk analysis and mitigation

### Multi-Tool
- Sequential tool chains
- Parallel tool usage
- Error recovery in workflows
- Research + analysis pipelines

### Reasoning
- Logical deduction
- Trade-off analysis
- Causal vs. correlation reasoning
- Hypothesis generation

### Refusals
- PII protection
- Malicious code detection
- Graceful limitation acknowledgment
- Medical/legal advice boundaries

### Communication
- Clarity and conciseness
- Technical accuracy with accessibility
- Adaptive tone for audiences
- Error communication

## 🔍 Understanding Results

### Test Statuses

- **PASS** ✓ - Completed successfully
- **PARTIAL** ~ - Partially completed or minor issues
- **FAIL** ✗ - Did not complete or major issues
- **REFUSED** ⊘ - Agent appropriately refused
- **ERROR** ! - Agent encountered errors
- **SKIPPED** - - Test was skipped

### Success Rate Calculation

```
Success Rate = (Pass + Partial × 0.5) / Total Attempted × 100%
```

Refusals and skipped tests don't count against success rate.

## 🛠️ CLI Options

```bash
python agent_tester.py [OPTIONS]

Options:
  --mode {interactive,automated,hybrid}
                        Test execution mode (default: interactive)
  --domain DOMAIN       Filter tests by domain
  --list-domains        List available test domains
  --agent-name NAME     Name of agent being tested
  --output FILENAME     Custom output filename for results
```

## 📊 Report Features

The HTML reports include:

1. **Summary Dashboard** - High-level metrics and success rates
2. **Domain Breakdown** - Performance by capability area
3. **Capability Matrix** - Visual heatmap of strengths/weaknesses
4. **Refusals Section** - Catalog of boundary tests
5. **Detailed Results** - Full test-by-test breakdown

## 🎯 Best Practices

1. **Start with Interactive Mode** - Understand agent behavior first
2. **Review Refusals Carefully** - Ensure they're appropriate
3. **Test Across All Domains** - Get comprehensive capability profile
4. **Generate Reports** - Track progress over time
5. **Customize Tests** - Add scenarios specific to your use case

## 📝 Example Session

```bash
# Run full test suite in interactive mode
python agent_tester.py --mode interactive --agent-name "Claude Code"

# [Work through tests with the agent]

# Generate HTML report
python generate_report.py test_results/test_results_20240109_143022.json

# Open report in browser
open test_results/test_results_20240109_143022_report.html
```

## 🔧 Troubleshooting

**No test scenarios found:**
- Ensure `test_scenarios/` directory exists
- Check YAML files are valid
- Run `--list-domains` to verify scenarios loaded

**Validation failing unexpectedly:**
- Check that test data files exist in `test_data/`
- Review validation patterns in scenario definitions
- Try interactive mode to manually assess

**Report generation errors:**
- Ensure results JSON file exists
- Check JSON is valid (not corrupted mid-test)
- Verify Python version is 3.8+

## 🚀 Advanced Usage

### Comparing Agent Versions

Run tests on different agent versions and compare:

```bash
# Test version 1
python agent_tester.py --agent-name "Agent-v1" --output agent_v1_results.json

# Test version 2
python agent_tester.py --agent-name "Agent-v2" --output agent_v2_results.json

# Generate comparative reports
python generate_report.py test_results/agent_v1_results.json
python generate_report.py test_results/agent_v2_results.json
```

### Creating Domain-Specific Test Suites

```bash
# Research-only tests
python agent_tester.py --domain research --output research_results.json

# Analysis-only tests
python agent_tester.py --domain analysis --output analysis_results.json
```

### Automated Regression Testing

For CI/CD pipelines:

```bash
# Run in automated mode with specific output
python agent_tester.py --mode automated --output nightly_test.json

# Generate report
python generate_report.py test_results/nightly_test.json nightly_report.html
```

## 📚 Resources

- **Test Scenario Schema**: See example scenarios in `test_scenarios/`
- **Evaluation Criteria**: Full rubrics in `evaluation_criteria.yaml`
- **Sample Data**: Realistic test data in `test_data/`

## 🤝 Contributing

To add new test scenarios:

1. Identify capability gap or new use case
2. Create test scenario in appropriate domain YAML
3. Add any required test data files
4. Test the scenario in interactive mode
5. Document expected behavior clearly

## 📄 License

This testing framework is provided as-is for evaluating AI agent capabilities.

## 🙏 Acknowledgments

Built to provide comprehensive, systematic evaluation of AI agents beyond coding tasks, focusing on the diverse capabilities needed for general-purpose assistance.

---

**Ready to test your agent?** Start with:
```bash
python agent_tester.py --mode interactive --agent-name "YourAgent"
```
