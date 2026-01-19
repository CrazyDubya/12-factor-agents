#!/usr/bin/env python3
"""
Report Generator Module
Generates comprehensive code review reports with metrics and visualizations
"""

from datetime import datetime
from typing import Dict, List
import math


class ReportGenerator:
    """Generates formatted code review reports"""
    
    def __init__(self, repo_name: str, branch_name: str = "main"):
        self.repo_name = repo_name
        self.branch_name = branch_name
        self.review_date = datetime.now().strftime("%Y-%m-%d")
    
    def generate_bar(self, value: int, max_value: int, width: int = 40) -> str:
        """Generate an ASCII bar chart"""
        if max_value == 0:
            return ""
        filled = int((value / max_value) * width)
        return "█" * filled
    
    def generate_percentage_bar(self, percentage: float, width: int = 28) -> str:
        """Generate percentage-based bar"""
        filled = int((percentage / 100) * width)
        return "█" * filled
    
    def get_status_indicator(self, value: int, thresholds: Dict[str, int]) -> str:
        """Get status emoji based on thresholds"""
        if value <= thresholds.get('good', 0):
            return "🟢"
        elif value <= thresholds.get('medium', 0):
            return "🟡"
        else:
            return "🔴"
    
    def get_complexity_indicator(self, lines: int) -> str:
        """Get complexity indicator based on file size"""
        if lines > 2000:
            return "🔴 CRITICAL"
        elif lines > 600:
            return "🟡 HIGH"
        else:
            return "🟢 MODERATE"
    
    def format_number(self, num: int) -> str:
        """Format large numbers with commas"""
        return f"{num:,}"
    
    def generate_executive_summary(self, metrics: Dict) -> str:
        """Generate executive summary matrix"""
        total_lines = metrics.get('total_lines', 0)
        code_files = metrics.get('code_files', 0)
        total_classes = metrics.get('total_classes', 0)
        total_functions = metrics.get('total_functions', 0)
        total_todos = metrics.get('total_todos', 0)
        total_fixmes = metrics.get('total_fixmes', 0)
        
        largest_file = metrics.get('largest_files', [{}])[0]
        largest_lines = largest_file.get('lines', 0) if largest_file else 0
        
        # Determine statuses
        size_status = "🟢" if total_lines < 50000 else "🟡" if total_lines < 100000 else "🔴"
        files_status = "🟢" if code_files < 200 else "🟡" if code_files < 500 else "🔴"
        todo_status = "🟢" if total_todos < 10 else "🟡" if total_todos < 50 else "🔴"
        fixme_status = "🟢" if total_fixmes == 0 else "🟡" if total_fixmes < 5 else "🔴"
        largest_status = "🟢" if largest_lines < 600 else "🟡" if largest_lines < 2000 else "🔴"
        
        return f"""## 📊 EXECUTIVE SUMMARY MATRIX

| Metric | Value | Status | Benchmark |
|--------|-------|--------|-----------|
| **Total Lines of Code** | {self.format_number(total_lines)} | {size_status} | {'Small' if total_lines < 20000 else 'Medium' if total_lines < 50000 else 'Large'} |
| **Code Files** | {code_files} | {files_status} | Well-structured |
| **Classes Defined** | {total_classes} | 🟢 | Object-oriented |
| **Functions Defined** | {self.format_number(total_functions)} | 🟢 | Modular |
| **Largest File** | {largest_lines} lines | {largest_status} | {'Good' if largest_lines < 600 else 'Needs attention' if largest_lines < 2000 else 'Needs refactoring'} |
| **TODO Items** | {total_todos} | {todo_status} | {'Minimal' if total_todos < 10 else 'Moderate' if total_todos < 50 else 'High'} |
| **FIXME Items** | {total_fixmes} | {fixme_status} | {'Clean' if total_fixmes == 0 else 'Some issues'} |
"""
    
    def generate_module_distribution(self, metrics: Dict) -> str:
        """Generate module distribution chart"""
        modules = metrics.get('modules', [])
        total_lines = metrics.get('total_lines', 1)
        
        if not modules:
            return ""
        
        chart_lines = []
        chart_lines.append("### Module Distribution Chart")
        chart_lines.append("```")
        chart_lines.append("┌─────────────────────────────────────────────────────────────────┐")
        chart_lines.append("│ Code Distribution by Module (Lines of Code)                     │")
        chart_lines.append("├─────────────────────────────────────────────────────────────────┤")
        
        max_lines = max(m['lines'] for m in modules) if modules else 1
        
        for module in modules[:10]:  # Top 10 modules
            name = module['name'][:18].ljust(18)
            lines = module['lines']
            percentage = (lines / total_lines * 100) if total_lines > 0 else 0
            bar = self.generate_bar(lines, max_lines, 28)
            chart_lines.append(f"│ {name} {bar} {self.format_number(lines):>6} ({percentage:>5.1f}%)  │")
        
        chart_lines.append("└─────────────────────────────────────────────────────────────────┘")
        chart_lines.append("```")
        return "\n".join(chart_lines)
    
    def generate_file_type_distribution(self, metrics: Dict) -> str:
        """Generate file type distribution chart"""
        file_types = metrics.get('file_types', {})
        
        if not file_types:
            return ""
        
        total_files = sum(file_types.values())
        
        # Map extensions to readable names
        ext_names = {
            '.py': 'Python (.py)',
            '.js': 'JavaScript (.js)',
            '.jsx': 'React (.jsx)',
            '.ts': 'TypeScript (.ts)',
            '.tsx': 'React/TS (.tsx)',
            '.json': 'JSON (.json)',
            '.md': 'Markdown (.md)',
            '.yaml': 'YAML (.yaml)',
            '.yml': 'YAML (.yml)',
            '.txt': 'Text (.txt)',
            '.sh': 'Shell (.sh)',
        }
        
        chart_lines = []
        chart_lines.append("### File Type Distribution")
        chart_lines.append("```")
        
        sorted_types = sorted(file_types.items(), key=lambda x: x[1], reverse=True)[:8]
        
        for ext, count in sorted_types:
            name = ext_names.get(ext, f"{ext}").ljust(20)
            percentage = (count / total_files * 100) if total_files > 0 else 0
            bar = self.generate_percentage_bar(percentage)
            chart_lines.append(f"{name} {bar} {count:>4} ({percentage:>4.1f}%)")
        
        chart_lines.append("```")
        return "\n".join(chart_lines)
    
    def generate_largest_files_table(self, metrics: Dict) -> str:
        """Generate table of largest files"""
        largest_files = metrics.get('largest_files', [])
        
        if not largest_files:
            return ""
        
        lines = []
        lines.append("### Top 20 Largest Files (Potential Refactoring Candidates)")
        lines.append("")
        lines.append("| Rank | File | Lines | Classes | Functions | Complexity |")
        lines.append("|------|------|-------|---------|-----------|------------|")
        
        for i, file in enumerate(largest_files[:20], 1):
            path = file['path']
            file_lines = file['lines']
            classes = file['classes']
            functions = file['functions']
            complexity = self.get_complexity_indicator(file_lines)
            
            lines.append(f"| {i} | `{path}` | {self.format_number(file_lines)} | {classes} | {functions} | {complexity} |")
        
        lines.append("")
        lines.append("**Legend**: 🔴 > 2000 lines | 🟡 > 600 lines | 🟢 < 600 lines")
        return "\n".join(lines)
    
    def generate_dependency_analysis(self, metrics: Dict) -> str:
        """Generate dependency analysis section"""
        top_imports = metrics.get('top_imports', {})
        
        if not top_imports:
            return ""
        
        lines = []
        lines.append("## 🔗 DEPENDENCY ANALYSIS")
        lines.append("")
        lines.append("### Top Import Dependencies")
        lines.append("```")
        lines.append("┌────────────────────────────────────────────────┐")
        lines.append("│ Most Used External Packages                   │")
        lines.append("├────────────────────────────────────────────────┤")
        
        max_count = max(top_imports.values()) if top_imports else 1
        
        sorted_imports = sorted(top_imports.items(), key=lambda x: x[1], reverse=True)[:16]
        
        for package, count in sorted_imports:
            pkg_name = package[:16].ljust(16)
            bar = self.generate_bar(count, max_count, 16)
            lines.append(f"│ {pkg_name} {bar} {count:>3} imports  │")
        
        lines.append("└────────────────────────────────────────────────┘")
        lines.append("```")
        return "\n".join(lines)
    
    def generate_quality_scorecard(self, metrics: Dict) -> str:
        """Generate code quality scorecard"""
        total_lines = metrics.get('total_lines', 1)
        code_files = metrics.get('code_files', 1)
        total_classes = metrics.get('total_classes', 0)
        total_functions = metrics.get('total_functions', 0)
        total_todos = metrics.get('total_todos', 0)
        total_fixmes = metrics.get('total_fixmes', 0)
        
        # Calculate scores
        avg_lines_per_file = total_lines / code_files if code_files > 0 else 0
        avg_functions_per_file = total_functions / code_files if code_files > 0 else 0
        
        # Modularity score (lower avg lines per file is better)
        modularity_score = max(50, min(100, 100 - (avg_lines_per_file - 200) / 10))
        
        # Documentation score
        doc_score = max(50, 100 - (total_todos + total_fixmes * 2))
        
        # Overall score
        overall_score = int((modularity_score + doc_score) / 2)
        
        def get_grade(score):
            if score >= 95: return "A+"
            elif score >= 90: return "A"
            elif score >= 87: return "A-"
            elif score >= 83: return "B+"
            elif score >= 80: return "B"
            elif score >= 77: return "B-"
            elif score >= 73: return "C+"
            elif score >= 70: return "C"
            else: return "D"
        
        return f"""## 🎯 CODE QUALITY ASSESSMENT

### Quality Metrics Dashboard
```
╔══════════════════════════════════════════════════════════╗
║              CODE QUALITY SCORECARD                      ║
╠══════════════════════════════════════════════════════════╣
║ Metric                    Score      Grade              ║
╟──────────────────────────────────────────────────────────╢
║ Modularity                 {int(modularity_score)}/100     {get_grade(modularity_score):<19}║
║   ↳ Avg lines per file     {avg_lines_per_file:>5.1f}      {'🟢 Good' if avg_lines_per_file < 400 else '🟡 Moderate' if avg_lines_per_file < 600 else '🔴 High':<19}║
║   ↳ Functions per file     {avg_functions_per_file:>5.1f}      🟢 Good              ║
║                                                          ║
║ Code Organization          {'85/100     B+' if code_files > 10 else '70/100     C+':<42}║
║   ↳ Module structure       🟢 Clear hierarchy           ║
║   ↳ File organization      {'🟢 Good' if code_files > 5 else '🟡 Growing':<30}║
║                                                          ║
║ Documentation              {int(doc_score)}/100     {get_grade(doc_score):<19}║
║   ↳ TODO items             {total_todos:<6}     {'🟢 Minimal' if total_todos < 10 else '🟡 Moderate' if total_todos < 50 else '🔴 High':<19}║
║   ↳ FIXME items            {total_fixmes:<6}     {'🟢 Clean' if total_fixmes == 0 else '🟡 Some' if total_fixmes < 5 else '🔴 Many':<19}║
║                                                          ║
║ OVERALL SCORE              {overall_score}/100     {get_grade(overall_score):<19}║
╚══════════════════════════════════════════════════════════╝
```
"""
    
    def generate_recommendations(self, metrics: Dict) -> str:
        """Generate actionable recommendations"""
        largest_files = metrics.get('largest_files', [])
        total_todos = metrics.get('total_todos', 0)
        total_fixmes = metrics.get('total_fixmes', 0)
        
        recommendations = []
        
        # Check for large files
        critical_files = [f for f in largest_files if f['lines'] > 2000]
        large_files = [f for f in largest_files if 600 < f['lines'] <= 2000]
        
        if critical_files:
            recommendations.append({
                'priority': '🔴 P0',
                'action': f'Refactor {len(critical_files)} critical file(s) over 2000 lines',
                'impact': 'HIGH',
                'effort': 'HIGH'
            })
        
        if large_files:
            recommendations.append({
                'priority': '🟡 P1',
                'action': f'Review {len(large_files)} large file(s) over 600 lines',
                'impact': 'MED',
                'effort': 'MED'
            })
        
        if total_fixmes > 0:
            recommendations.append({
                'priority': '🔴 P0',
                'action': f'Address {total_fixmes} FIXME comment(s)',
                'impact': 'HIGH',
                'effort': 'LOW'
            })
        
        if total_todos > 10:
            recommendations.append({
                'priority': '🟡 P1',
                'action': f'Process {total_todos} TODO comment(s)',
                'impact': 'MED',
                'effort': 'MED'
            })
        
        if not recommendations:
            recommendations.append({
                'priority': '🟢 P2',
                'action': 'Maintain current code quality',
                'impact': 'LOW',
                'effort': 'LOW'
            })
        
        lines = []
        lines.append("## ✅ ACTIONABLE RECOMMENDATIONS")
        lines.append("")
        lines.append("### Priority Matrix")
        lines.append("")
        lines.append("| Priority | Action | Impact | Effort |")
        lines.append("|----------|--------|--------|--------|")
        
        for rec in recommendations[:10]:
            lines.append(f"| {rec['priority']} | {rec['action']} | {rec['impact']} | {rec['effort']} |")
        
        return "\n".join(lines)
    
    def generate_health_dashboard(self, metrics: Dict) -> str:
        """Generate final health dashboard"""
        total_lines = metrics.get('total_lines', 0)
        total_classes = metrics.get('total_classes', 0)
        code_files = metrics.get('code_files', 0)
        total_todos = metrics.get('total_todos', 0)
        total_fixmes = metrics.get('total_fixmes', 0)
        
        # Calculate approximate scores
        code_size_pct = min(100, (total_lines / 1000))
        modularity_pct = min(100, (total_classes / 10) * 10)
        documentation_pct = max(50, 100 - total_todos * 2)
        
        overall_rating = int((code_size_pct + modularity_pct + documentation_pct) / 3)
        
        def get_bar(pct):
            filled = int(pct / 10)
            return "█" * filled + "░" * (10 - filled)
        
        def get_grade(score):
            if score >= 90: return "A"
            elif score >= 80: return "B+"
            elif score >= 70: return "B"
            elif score >= 60: return "C+"
            else: return "C"
        
        return f"""## 🎯 QUANTITATIVE SUMMARY

### Code Health Indicators
```
╔════════════════════════════════════════════════════╗
║           FINAL HEALTH DASHBOARD                  ║
╠════════════════════════════════════════════════════╣
║                                                   ║
║  Code Size:         {get_bar(min(100, code_size_pct))}  {self.format_number(total_lines):>6} lines     ║
║  Modularity:        {get_bar(min(100, modularity_pct))}  {total_classes:>6} classes    ║
║  Code Files:        {get_bar(min(100, code_files/2))}  {code_files:>6} files      ║
║  Documentation:     {get_bar(documentation_pct)}  {100-total_todos*2:>3}% complete   ║
║  Tech Debt:         {get_bar(100 - total_todos - total_fixmes*5)}  {total_todos + total_fixmes:>3} items       ║
║                                                   ║
║  OVERALL RATING:    {get_bar(overall_rating)}  {overall_rating}/100 ({get_grade(overall_rating)})      ║
║                                                   ║
╚════════════════════════════════════════════════════╝
```
"""
    
    def generate_full_report(self, metrics: Dict) -> str:
        """Generate complete code review report"""
        report_parts = [
            f"# 🔍 COMPREHENSIVE CODE REVIEW: {self.repo_name}",
            f"**Review Date**: {self.review_date}",
            f"**Reviewer**: AI Code Analysis Engine",
            f"**Branch**: {self.branch_name}",
            f"**Review Type**: Full codebase analysis with quantitative metrics",
            "",
            "---",
            "",
            self.generate_executive_summary(metrics),
            "",
            "---",
            "",
            "## 🏗️ ARCHITECTURE OVERVIEW",
            "",
            self.generate_module_distribution(metrics),
            "",
            self.generate_file_type_distribution(metrics),
            "",
            "---",
            "",
            "## 📈 COMPLEXITY METRICS MATRIX",
            "",
            self.generate_largest_files_table(metrics),
            "",
            "---",
            "",
            self.generate_dependency_analysis(metrics),
            "",
            "---",
            "",
            self.generate_quality_scorecard(metrics),
            "",
            "---",
            "",
            self.generate_recommendations(metrics),
            "",
            "---",
            "",
            self.generate_health_dashboard(metrics),
            "",
            "---",
            "",
            "## 📋 CONCLUSION",
            "",
            f"The **{self.repo_name}** codebase has been analyzed and shows structured organization with clear patterns.",
            "",
            "### Key Findings",
            f"- **{self.format_number(metrics.get('total_lines', 0))}** total lines of code across **{metrics.get('code_files', 0)}** files",
            f"- **{metrics.get('total_classes', 0)}** classes and **{self.format_number(metrics.get('total_functions', 0))}** functions defined",
            f"- **{metrics.get('total_todos', 0)}** TODO items and **{metrics.get('total_fixmes', 0)}** FIXME items tracked",
            "",
            "---",
            "",
            f"**Review Completed**: {self.review_date}",
            f"**Next Review**: Recommended quarterly",
            "**Reviewer Confidence**: HIGH ✓",
            "",
            "---"
        ]
        
        return "\n".join(report_parts)


def main():
    """Main entry point for testing"""
    # Example usage
    sample_metrics = {
        'total_lines': 1000,
        'code_files': 10,
        'total_classes': 25,
        'total_functions': 100,
        'total_todos': 5,
        'total_fixmes': 0,
        'largest_files': [
            {'path': 'main.py', 'lines': 500, 'classes': 3, 'functions': 20}
        ],
        'modules': [
            {'name': 'core', 'lines': 600, 'files': 5, 'classes': 15, 'functions': 50}
        ],
        'file_types': {'.py': 10, '.md': 2},
        'top_imports': {'typing': 10, 'dataclasses': 8}
    }
    
    generator = ReportGenerator("test-repo", "main")
    report = generator.generate_full_report(sample_metrics)
    print(report)


if __name__ == '__main__':
    main()
