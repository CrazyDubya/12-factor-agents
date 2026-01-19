# Code Review Report Generator

A comprehensive code analysis and review report generator that produces detailed metrics, visualizations, and actionable recommendations for any codebase.

## 🎯 Overview

This tool analyzes your repository's structure and generates a professional code review report similar to those produced by senior engineering teams. The report includes:

- **Quantitative Metrics**: Lines of code, file counts, complexity measurements
- **Visual Charts**: ASCII-based charts and graphs for easy visualization
- **Architecture Analysis**: Module distribution and dependency analysis
- **Quality Scorecard**: Comprehensive quality metrics with grades
- **Actionable Recommendations**: Prioritized list of improvements
- **Health Dashboard**: Overall codebase health indicators

## 📋 Features

### Analysis Capabilities

- ✅ Multi-language support (Python, JavaScript, TypeScript, Java, Go, Rust, Ruby)
- ✅ File and module metrics (LOC, classes, functions)
- ✅ Dependency analysis (import tracking)
- ✅ Code organization patterns
- ✅ TODO/FIXME detection
- ✅ Complexity indicators
- ✅ File size distribution

### Report Components

1. **Executive Summary Matrix** - High-level metrics with status indicators
2. **Architecture Overview** - Module distribution and file type breakdown
3. **Complexity Metrics** - Largest files and potential refactoring candidates
4. **Dependency Analysis** - Most used packages and imports
5. **Quality Assessment** - Scorecard with grades for different aspects
6. **Recommendations** - Prioritized action items with impact/effort estimates
7. **Health Dashboard** - Visual representation of overall code health

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- No external dependencies required (uses only standard library)

### Basic Usage

```bash
# Analyze current directory
python generate_review_report.py

# Analyze a specific repository
python generate_review_report.py /path/to/repository

# Specify output file
python generate_review_report.py /path/to/repo -o my_report.md

# Include branch name in report
python generate_review_report.py . -b develop

# Specify custom repository name
python generate_review_report.py . -n "My Project"
```

### Advanced Options

```bash
# Full command with all options
python generate_review_report.py /path/to/repo \
    --output CUSTOM_REPORT.md \
    --branch feature/my-branch \
    --name "My Amazing Project" \
    --exclude temp artifacts backup
```

### Command-Line Arguments

| Argument | Short | Description | Default |
|----------|-------|-------------|---------|
| `repository_path` | - | Path to repository | Current directory |
| `--output` | `-o` | Output file path | `CODE_REVIEW_REPORT.md` |
| `--branch` | `-b` | Branch name for report | `main` |
| `--name` | `-n` | Repository name | Directory name |
| `--exclude` | - | Additional dirs to exclude | None |

## 📊 Report Example

The generated report includes sections like:

```markdown
# 🔍 COMPREHENSIVE CODE REVIEW: YourProject

## 📊 EXECUTIVE SUMMARY MATRIX

| Metric | Value | Status | Benchmark |
|--------|-------|--------|-----------|
| **Total Lines of Code** | 15,432 | 🟢 | Medium |
| **Code Files** | 89 | 🟢 | Well-structured |
| **Classes Defined** | 156 | 🟢 | Object-oriented |
...

## 🏗️ ARCHITECTURE OVERVIEW

### Module Distribution Chart
┌─────────────────────────────────────────────────────────────────┐
│ Code Distribution by Module (Lines of Code)                     │
├─────────────────────────────────────────────────────────────────┤
│ core              ████████████████████████████ 4,523 (29.3%)   │
│ utils             ███████████████              2,156 (14.0%)   │
...
```

## 🔧 Architecture

### Components

1. **`code_analyzer.py`** - Core analysis engine
   - Walks repository tree
   - Parses code files
   - Extracts metrics (LOC, classes, functions, imports)
   - Aggregates by module

2. **`report_generator.py`** - Report formatting engine
   - Generates ASCII charts and tables
   - Calculates quality scores
   - Formats markdown output
   - Creates visualizations

3. **`generate_review_report.py`** - Main CLI interface
   - Parses command-line arguments
   - Orchestrates analysis and reporting
   - Handles file I/O

### Design Principles

- **No External Dependencies**: Uses only Python standard library
- **Extensible**: Easy to add new languages or metrics
- **Fast**: Efficient file system traversal and analysis
- **Portable**: Works on any platform with Python

## 📝 Supported Languages

### Full Analysis Support
- Python (`.py`)
- JavaScript (`.js`, `.jsx`)
- TypeScript (`.ts`, `.tsx`)

### Partial Analysis Support
- Java (`.java`)
- Go (`.go`)
- Rust (`.rs`)
- Ruby (`.rb`)

Note: For languages without full support, the tool still counts lines of code.

## 🎨 Customization

### Excluding Directories

By default, the following directories are excluded:
- `.git`, `__pycache__`, `node_modules`
- `.venv`, `venv`, `.pytest_cache`
- `dist`, `build`, `.cache`
- And other common build/cache directories

Add more exclusions:
```bash
python generate_review_report.py . --exclude tmp vendor third_party
```

### Adding New Languages

To add support for a new language, edit `code_analyzer.py`:

1. Add a new method like `analyze_<language>_file()`
2. Update `analyze_file()` to handle the new extension
3. Implement patterns for class/function detection

Example:
```python
def analyze_ruby_file(self, file_path: Path) -> FileMetrics:
    # Add Ruby-specific parsing logic
    class_pattern = re.compile(r'^\s*class\s+\w+')
    func_pattern = re.compile(r'^\s*def\s+\w+')
    # ... rest of implementation
```

## 📈 Metrics Explained

### Lines of Code (LOC)
- Total number of lines in code files
- Excludes blank lines and pure comment lines in Python/JS

### Complexity Indicators
- 🟢 **MODERATE**: < 600 lines per file
- 🟡 **HIGH**: 600-2000 lines per file
- 🔴 **CRITICAL**: > 2000 lines per file

### Quality Score Components
1. **Modularity** (50%): Based on average file size
2. **Documentation** (50%): Based on TODO/FIXME count

### Status Indicators
- 🟢 **Green**: Good/Acceptable
- 🟡 **Yellow**: Needs attention
- 🔴 **Red**: Critical/Urgent

## 🧪 Testing

Run the analyzer on itself:
```bash
python generate_review_report.py . -n "Code Review Generator" -o SELF_REVIEW.md
```

This will generate a report analyzing this tool's own codebase!

## 🤝 Contributing

Ideas for contributions:
1. Add support for more programming languages
2. Implement additional metrics (cyclomatic complexity, test coverage)
3. Add configuration file support (`.reviewrc.json`)
4. Create HTML output format
5. Add git integration (commit analysis, contributor stats)
6. Implement trend tracking (compare multiple reports)

## 📄 License

This code review tool is provided as-is for analyzing codebases and generating reports.

## 🔮 Future Enhancements

Planned features:
- [ ] HTML/PDF output formats
- [ ] Git history analysis
- [ ] Test coverage integration
- [ ] Cyclomatic complexity calculation
- [ ] Code duplication detection
- [ ] Security vulnerability scanning
- [ ] Performance profiling integration
- [ ] Trend tracking across multiple runs
- [ ] Interactive web dashboard

## 📚 Example Use Cases

### Before Major Refactoring
```bash
python generate_review_report.py . -o before_refactor.md -b develop
# Make changes...
python generate_review_report.py . -o after_refactor.md -b develop
# Compare reports to measure improvement
```

### CI/CD Integration
```bash
# In your CI pipeline
python generate_review_report.py . -o reports/review_${BUILD_ID}.md
# Archive report as build artifact
```

### Code Review Preparation
```bash
# Generate report before PR review
python generate_review_report.py . -b feature/new-feature -o pr_review.md
# Attach report to PR description
```

## 🙋 FAQ

**Q: Does this tool modify my code?**  
A: No, it only reads files and generates a report. It never modifies your code.

**Q: How long does analysis take?**  
A: Usually a few seconds for small projects, up to a minute for very large codebases (100k+ LOC).

**Q: Can I run this on private repositories?**  
A: Yes, the tool runs locally and doesn't send data anywhere.

**Q: What if my language isn't supported?**  
A: The tool will still count lines of code and file types. Full analysis (classes/functions) requires language-specific support.

**Q: Can I use this in CI/CD?**  
A: Absolutely! The tool exits with status code 0 on success, making it perfect for automated pipelines.

## 📞 Support

For issues or questions:
1. Check this README
2. Review the example output
3. Run with `--help` for command-line options

---

**Happy Analyzing! 🚀**
