# Code Review Report Generator - Quick Start Guide

## What Is This?

A comprehensive code analysis tool that generates professional code review reports with metrics, visualizations, and recommendations - similar to reports produced by senior engineering teams.

## Quick Start

### 1. Run the Analysis

```bash
python generate_review_report.py
```

This will analyze your current directory and create `CODE_REVIEW_REPORT.md`.

### 2. View the Report

Open `CODE_REVIEW_REPORT.md` to see:
- 📊 Executive summary with key metrics
- 🏗️ Architecture overview with charts
- 📈 Complexity analysis
- 🔗 Dependency tracking
- 🎯 Quality scorecard
- ✅ Actionable recommendations
- 💯 Health dashboard

### 3. Customize Your Analysis

```bash
# Analyze a specific directory
python generate_review_report.py /path/to/project

# Custom output file
python generate_review_report.py -o my_report.md

# Specify branch and project name
python generate_review_report.py -b develop -n "My Project"

# Exclude additional directories
python generate_review_report.py --exclude vendor tmp build
```

## Example Output

See [examples/EXAMPLE_REPORT.md](examples/EXAMPLE_REPORT.md) for a complete sample report.

## What Gets Analyzed?

- **Languages**: Python, JavaScript, TypeScript, Java, Go, Rust, Ruby
- **Metrics**: Lines of code, classes, functions, imports
- **Quality**: TODO/FIXME items, file sizes, code organization
- **Architecture**: Module distribution, dependency patterns

## Report Sections

1. **Executive Summary** - Overview of key metrics
2. **Architecture** - Code distribution by module
3. **Complexity** - Largest files that may need refactoring
4. **Dependencies** - Most used packages
5. **Quality Score** - Letter grade assessment
6. **Recommendations** - Prioritized action items
7. **Health Dashboard** - Visual code health indicators

## Requirements

- Python 3.7+
- No external dependencies needed!

## Tips

- Run before major refactoring to track improvements
- Include in CI/CD for automated code quality tracking
- Generate regularly to track technical debt trends
- Share with team for code review discussions

## Learn More

- [README.md](README.md) - Full documentation
- [examples/EXAMPLE_REPORT.md](examples/EXAMPLE_REPORT.md) - Sample output
- [CODE_REVIEW_REPORT.md](CODE_REVIEW_REPORT.md) - Self-analysis

## Need Help?

Run `python generate_review_report.py --help` for all options.

---

**Happy Analyzing! 🚀**
