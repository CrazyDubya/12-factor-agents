#!/usr/bin/env python3
"""
Code Analyzer Module
Analyzes repository structure and generates comprehensive metrics
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Set
from collections import defaultdict, Counter
from dataclasses import dataclass, field
import json


@dataclass
class FileMetrics:
    """Metrics for a single file"""
    path: str
    lines: int
    classes: int
    functions: int
    imports: List[str] = field(default_factory=list)
    todos: int = 0
    fixmes: int = 0


@dataclass
class ModuleMetrics:
    """Metrics for a module/directory"""
    name: str
    files: int = 0
    lines: int = 0
    classes: int = 0
    functions: int = 0


class CodeAnalyzer:
    """Analyzes code repository structure and metrics"""
    
    def __init__(self, root_path: str, exclude_dirs: Set[str] = None):
        self.root_path = Path(root_path)
        self.exclude_dirs = exclude_dirs or {
            '.git', '__pycache__', 'node_modules', '.venv', 'venv',
            '.pytest_cache', '.mypy_cache', 'dist', 'build', '.cache',
            '.egg-info', 'htmlcov', '.tox'
        }
        self.file_metrics: List[FileMetrics] = []
        self.module_metrics: Dict[str, ModuleMetrics] = {}
        
    def should_exclude(self, path: Path) -> bool:
        """Check if path should be excluded"""
        parts = path.parts
        return any(excluded in parts for excluded in self.exclude_dirs)
    
    def analyze_python_file(self, file_path: Path) -> FileMetrics:
        """Analyze a Python file for metrics"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return FileMetrics(path=str(file_path), lines=0, classes=0, functions=0)
        
        
        # Count classes
        class_pattern = re.compile(r'^\s*class\s+\w+')
        classes = sum(1 for line in lines if class_pattern.match(line))
        
        # Count functions and methods
        func_pattern = re.compile(r'^\s*def\s+\w+')
        functions = sum(1 for line in lines if func_pattern.match(line))
        
        # Extract imports
        import_pattern = re.compile(r'^\s*(?:from\s+([\w.]+)\s+)?import\s+([\w.,\s]+)')
        imports = []
        for line in lines:
            match = import_pattern.match(line)
            if match:
                if match.group(1):  # from X import Y
                    imports.append(match.group(1).split('.')[0])
                else:  # import X
                    for imp in match.group(2).split(','):
                        imports.append(imp.strip().split('.')[0])
        
        # Count TODOs and FIXMEs
        todos = sum(1 for line in lines if 'TODO' in line.upper())
        fixmes = sum(1 for line in lines if 'FIXME' in line.upper())
        
        return FileMetrics(
            path=str(file_path.relative_to(self.root_path)),
            lines=len(lines),
            classes=classes,
            functions=functions,
            imports=imports,
            todos=todos,
            fixmes=fixmes
        )
    
    def analyze_javascript_file(self, file_path: Path) -> FileMetrics:
        """Analyze a JavaScript/TypeScript file for metrics"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return FileMetrics(path=str(file_path), lines=0, classes=0, functions=0)
        
        # Count classes
        class_pattern = re.compile(r'^\s*(?:export\s+)?(?:default\s+)?class\s+\w+')
        classes = sum(1 for line in lines if class_pattern.match(line))
        
        # Count functions (matches: function declarations, arrow functions, async variants)
        # Examples: "export function foo()", "const bar = () =>", "async function baz()"
        func_pattern = re.compile(r'^\s*(?:export\s+)?(?:async\s+)?(?:function\s+\w+|const\s+\w+\s*=\s*(?:async\s+)?.*=>)')
        functions = sum(1 for line in lines if func_pattern.match(line))
        
        # Extract imports
        import_pattern = re.compile(r'^\s*import\s+.*from\s+[\'"](.+?)[\'"]')
        imports = []
        for line in lines:
            match = import_pattern.match(line)
            if match:
                imp = match.group(1)
                if not imp.startswith('.'):  # External import
                    imports.append(imp.split('/')[0])
        
        # Count TODOs and FIXMEs
        todos = sum(1 for line in lines if 'TODO' in line.upper())
        fixmes = sum(1 for line in lines if 'FIXME' in line.upper())
        
        return FileMetrics(
            path=str(file_path.relative_to(self.root_path)),
            lines=len(lines),
            classes=classes,
            functions=functions,
            imports=imports,
            todos=todos,
            fixmes=fixmes
        )
    
    def analyze_file(self, file_path: Path) -> FileMetrics:
        """Analyze a file based on its extension"""
        ext = file_path.suffix.lower()
        
        if ext == '.py':
            return self.analyze_python_file(file_path)
        elif ext in ['.js', '.jsx', '.ts', '.tsx']:
            return self.analyze_javascript_file(file_path)
        else:
            # Just count lines for other files
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = len(f.readlines())
            except:
                lines = 0
            return FileMetrics(
                path=str(file_path.relative_to(self.root_path)),
                lines=lines,
                classes=0,
                functions=0
            )
    
    def analyze_repository(self) -> Dict[str, any]:
        """Analyze entire repository and return comprehensive metrics"""
        print(f"Analyzing repository at: {self.root_path}")
        
        # File type counters
        file_types = Counter()
        total_files = 0
        
        # Walk through repository
        for root, dirs, files in os.walk(self.root_path):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
            
            root_path = Path(root)
            if self.should_exclude(root_path):
                continue
            
            for file in files:
                file_path = root_path / file
                total_files += 1
                
                # Count file types
                ext = file_path.suffix.lower()
                if ext:
                    file_types[ext] += 1
                
                # Analyze code files
                if ext in ['.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.go', '.rs', '.rb']:
                    metrics = self.analyze_file(file_path)
                    self.file_metrics.append(metrics)
                    
                    # Aggregate by module
                    module_name = str(file_path.parent.relative_to(self.root_path))
                    if module_name == '.':
                        module_name = 'root'
                    
                    if module_name not in self.module_metrics:
                        self.module_metrics[module_name] = ModuleMetrics(name=module_name)
                    
                    mod = self.module_metrics[module_name]
                    mod.files += 1
                    mod.lines += metrics.lines
                    mod.classes += metrics.classes
                    mod.functions += metrics.functions
        
        return self.compile_results(file_types, total_files)
    
    def compile_results(self, file_types: Counter, total_files: int) -> Dict:
        """Compile all analysis results"""
        # Sort files by size
        sorted_files = sorted(self.file_metrics, key=lambda x: x.lines, reverse=True)
        
        # Calculate totals
        total_lines = sum(f.lines for f in self.file_metrics)
        total_classes = sum(f.classes for f in self.file_metrics)
        total_functions = sum(f.functions for f in self.file_metrics)
        total_todos = sum(f.todos for f in self.file_metrics)
        total_fixmes = sum(f.fixmes for f in self.file_metrics)
        
        # Aggregate imports
        all_imports = []
        for f in self.file_metrics:
            all_imports.extend(f.imports)
        import_counts = Counter(all_imports)
        
        # Sort modules by lines
        sorted_modules = sorted(
            self.module_metrics.values(),
            key=lambda x: x.lines,
            reverse=True
        )
        
        return {
            'total_files': total_files,
            'code_files': len(self.file_metrics),
            'total_lines': total_lines,
            'total_classes': total_classes,
            'total_functions': total_functions,
            'total_todos': total_todos,
            'total_fixmes': total_fixmes,
            'file_types': dict(file_types.most_common()),
            'largest_files': [
                {
                    'path': f.path,
                    'lines': f.lines,
                    'classes': f.classes,
                    'functions': f.functions
                }
                for f in sorted_files[:20]
            ],
            'modules': [
                {
                    'name': m.name,
                    'files': m.files,
                    'lines': m.lines,
                    'classes': m.classes,
                    'functions': m.functions
                }
                for m in sorted_modules[:15]
            ],
            'top_imports': dict(import_counts.most_common(20)),
        }


def main():
    """Main entry point for testing"""
    import sys
    
    if len(sys.argv) > 1:
        repo_path = sys.argv[1]
    else:
        repo_path = '.'
    
    analyzer = CodeAnalyzer(repo_path)
    results = analyzer.analyze_repository()
    
    print(json.dumps(results, indent=2))


if __name__ == '__main__':
    main()
