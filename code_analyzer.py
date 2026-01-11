"""
ATENA Framework - Code Analyzer Module
Analyzes code files and suggests refactoring improvements.
"""
import ast
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import CODE_EXTENSIONS, MAX_FUNCTION_LENGTH, MAX_COMPLEXITY
from core.logger import setup_logger, log_operation

logger = setup_logger("code_analyzer")


@dataclass
class CodeIssue:
    """Represents a code quality issue."""
    file: str
    line: int
    issue_type: str
    severity: str  # LOW, MEDIUM, HIGH
    message: str
    suggestion: str


@dataclass
class AnalysisResult:
    """Results from analyzing a file."""
    file_path: str
    issues: list[CodeIssue] = field(default_factory=list)
    metrics: dict = field(default_factory=dict)


class PythonAnalyzer:
    """Analyzes Python code for quality issues."""

    def analyze(self, file_path: Path) -> AnalysisResult:
        """Analyze a Python file for code quality issues."""
        result = AnalysisResult(file_path=str(file_path))

        try:
            content = file_path.read_text()
            tree = ast.parse(content)
        except SyntaxError as e:
            result.issues.append(CodeIssue(
                file=str(file_path),
                line=e.lineno or 0,
                issue_type="SYNTAX_ERROR",
                severity="HIGH",
                message=f"Syntax error: {e.msg}",
                suggestion="Fix the syntax error before proceeding"
            ))
            return result

        lines = content.split("\n")
        result.metrics["total_lines"] = len(lines)
        result.metrics["blank_lines"] = sum(1 for line in lines if not line.strip())
        result.metrics["comment_lines"] = sum(1 for line in lines if line.strip().startswith("#"))

        # Analyze functions
        self._analyze_functions(tree, file_path, result)

        # Analyze classes
        self._analyze_classes(tree, file_path, result)

        # Check for common issues
        self._check_common_issues(content, file_path, result)

        return result

    def _analyze_functions(self, tree: ast.AST, file_path: Path, result: AnalysisResult) -> None:
        """Analyze function definitions."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check function length
                func_lines = node.end_lineno - node.lineno + 1 if node.end_lineno else 0
                if func_lines > MAX_FUNCTION_LENGTH:
                    result.issues.append(CodeIssue(
                        file=str(file_path),
                        line=node.lineno,
                        issue_type="LONG_FUNCTION",
                        severity="MEDIUM",
                        message=f"Function '{node.name}' has {func_lines} lines (max: {MAX_FUNCTION_LENGTH})",
                        suggestion="Consider breaking this function into smaller, focused functions"
                    ))

                # Check for missing docstring
                if not ast.get_docstring(node):
                    result.issues.append(CodeIssue(
                        file=str(file_path),
                        line=node.lineno,
                        issue_type="MISSING_DOCSTRING",
                        severity="LOW",
                        message=f"Function '{node.name}' lacks a docstring",
                        suggestion="Add a docstring describing the function's purpose and parameters"
                    ))

                # Check parameter count
                param_count = len(node.args.args)
                if param_count > 5:
                    result.issues.append(CodeIssue(
                        file=str(file_path),
                        line=node.lineno,
                        issue_type="TOO_MANY_PARAMETERS",
                        severity="MEDIUM",
                        message=f"Function '{node.name}' has {param_count} parameters",
                        suggestion="Consider using a configuration object or dataclass to group parameters"
                    ))

                # Calculate cyclomatic complexity
                complexity = self._calculate_complexity(node)
                if complexity > MAX_COMPLEXITY:
                    result.issues.append(CodeIssue(
                        file=str(file_path),
                        line=node.lineno,
                        issue_type="HIGH_COMPLEXITY",
                        severity="HIGH",
                        message=f"Function '{node.name}' has complexity {complexity} (max: {MAX_COMPLEXITY})",
                        suggestion="Reduce complexity by extracting conditions into separate functions"
                    ))

    def _analyze_classes(self, tree: ast.AST, file_path: Path, result: AnalysisResult) -> None:
        """Analyze class definitions."""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check for missing class docstring
                if not ast.get_docstring(node):
                    result.issues.append(CodeIssue(
                        file=str(file_path),
                        line=node.lineno,
                        issue_type="MISSING_DOCSTRING",
                        severity="LOW",
                        message=f"Class '{node.name}' lacks a docstring",
                        suggestion="Add a docstring describing the class's purpose"
                    ))

                # Count methods
                methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                if len(methods) > 20:
                    result.issues.append(CodeIssue(
                        file=str(file_path),
                        line=node.lineno,
                        issue_type="LARGE_CLASS",
                        severity="MEDIUM",
                        message=f"Class '{node.name}' has {len(methods)} methods",
                        suggestion="Consider splitting into smaller, focused classes (Single Responsibility)"
                    ))

    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity of a function."""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity

    def _check_common_issues(self, content: str, file_path: Path, result: AnalysisResult) -> None:
        """Check for common code issues."""
        lines = content.split("\n")

        for i, line in enumerate(lines, 1):
            # Check line length
            if len(line) > 120:
                result.issues.append(CodeIssue(
                    file=str(file_path),
                    line=i,
                    issue_type="LINE_TOO_LONG",
                    severity="LOW",
                    message=f"Line exceeds 120 characters ({len(line)} chars)",
                    suggestion="Break the line into multiple lines for better readability"
                ))

            # Check for TODO/FIXME comments
            if re.search(r"#\s*(TODO|FIXME|XXX|HACK)", line, re.IGNORECASE):
                result.issues.append(CodeIssue(
                    file=str(file_path),
                    line=i,
                    issue_type="PENDING_TASK",
                    severity="LOW",
                    message="Found pending task marker",
                    suggestion="Address or track this task in your issue tracker"
                ))

            # Check for bare except
            if re.search(r"except\s*:", line):
                result.issues.append(CodeIssue(
                    file=str(file_path),
                    line=i,
                    issue_type="BARE_EXCEPT",
                    severity="HIGH",
                    message="Bare except clause catches all exceptions",
                    suggestion="Specify the exception type(s) to catch"
                ))

            # Check for print statements (should use logging)
            if re.search(r"^\s*print\s*\(", line) and "# noqa" not in line:
                result.issues.append(CodeIssue(
                    file=str(file_path),
                    line=i,
                    issue_type="PRINT_STATEMENT",
                    severity="LOW",
                    message="Using print() instead of logging",
                    suggestion="Consider using the logging module for better control"
                ))


class CodeAnalyzer:
    """Main code analyzer that delegates to language-specific analyzers."""

    def __init__(self):
        self.analyzers = {
            ".py": PythonAnalyzer(),
        }

    def analyze_file(self, file_path: str | Path) -> Optional[AnalysisResult]:
        """Analyze a single file."""
        path = Path(file_path)

        if not path.exists():
            logger.error(f"File not found: {path}")
            return None

        if path.suffix not in self.analyzers:
            logger.warning(f"No analyzer available for {path.suffix} files")
            return None

        log_operation("analyze_file", "STARTED", str(path))
        result = self.analyzers[path.suffix].analyze(path)
        log_operation("analyze_file", "COMPLETED", f"Found {len(result.issues)} issues")

        return result

    def analyze_path(self, path: str | Path) -> list[AnalysisResult]:
        """Analyze all supported files in a path (file or directory)."""
        path = Path(path)
        results = []

        if path.is_file():
            result = self.analyze_file(path)
            if result:
                results.append(result)
        elif path.is_dir():
            for ext in self.analyzers.keys():
                for file_path in path.rglob(f"*{ext}"):
                    # Skip virtual environments and cache
                    if any(skip in str(file_path) for skip in ["venv", "__pycache__", ".git", "node_modules"]):
                        continue
                    result = self.analyze_file(file_path)
                    if result:
                        results.append(result)

        return results

    def print_report(self, results: list[AnalysisResult]) -> None:
        """Print a formatted analysis report."""
        total_issues = sum(len(r.issues) for r in results)

        print("\n" + "=" * 60)
        print("ATENA CODE ANALYSIS REPORT")
        print("=" * 60)

        if not results:
            print("\nNo files analyzed.")
            return

        print(f"\nFiles analyzed: {len(results)}")
        print(f"Total issues found: {total_issues}")

        severity_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for result in results:
            for issue in result.issues:
                severity_counts[issue.severity] += 1

        print(f"\nBy severity:")
        print(f"  🔴 HIGH:   {severity_counts['HIGH']}")
        print(f"  🟡 MEDIUM: {severity_counts['MEDIUM']}")
        print(f"  🟢 LOW:    {severity_counts['LOW']}")

        for result in results:
            if result.issues:
                print(f"\n{'─' * 60}")
                print(f"📄 {result.file_path}")
                if result.metrics:
                    print(f"   Lines: {result.metrics.get('total_lines', 'N/A')}")

                for issue in sorted(result.issues, key=lambda x: x.line):
                    severity_icon = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}[issue.severity]
                    print(f"\n   {severity_icon} Line {issue.line}: [{issue.issue_type}]")
                    print(f"      {issue.message}")
                    print(f"      💡 {issue.suggestion}")

        print("\n" + "=" * 60)


if __name__ == "__main__":
    import sys
    analyzer = CodeAnalyzer()
    path = sys.argv[1] if len(sys.argv) > 1 else "."
    results = analyzer.analyze_path(path)
    analyzer.print_report(results)
