"""
ATENA Framework - Documentation Fetcher Module
Fetches API documentation when errors occur during development.
"""
import re
from dataclasses import dataclass
from typing import Optional
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import DOC_SOURCES
from core.logger import setup_logger, log_operation

logger = setup_logger("doc_fetcher")


@dataclass
class ErrorInfo:
    """Parsed error information."""
    error_type: str
    message: str
    module: Optional[str] = None
    function: Optional[str] = None
    line_number: Optional[int] = None


@dataclass
class DocReference:
    """Documentation reference for an error."""
    title: str
    url: str
    description: str
    related_topics: list[str]


class ErrorParser:
    """Parses error messages to extract relevant information."""

    # Common Python error patterns
    ERROR_PATTERNS = {
        "import": r"(?:ModuleNotFoundError|ImportError):\s*(?:No module named\s*)?['\"]?(\w+)['\"]?",
        "attribute": r"AttributeError:\s*['\"]?(\w+)['\"]?\s*object has no attribute\s*['\"]?(\w+)['\"]?",
        "type": r"TypeError:\s*(.+)",
        "name": r"NameError:\s*name\s*['\"]?(\w+)['\"]?\s*is not defined",
        "value": r"ValueError:\s*(.+)",
        "key": r"KeyError:\s*['\"]?(.+?)['\"]?",
        "index": r"IndexError:\s*(.+)",
        "syntax": r"SyntaxError:\s*(.+)",
    }

    def parse(self, error_output: str) -> Optional[ErrorInfo]:
        """Parse error output and extract structured information."""
        for error_type, pattern in self.ERROR_PATTERNS.items():
            match = re.search(pattern, error_output)
            if match:
                return ErrorInfo(
                    error_type=error_type,
                    message=match.group(0),
                    module=match.group(1) if match.lastindex >= 1 else None,
                    function=match.group(2) if match.lastindex >= 2 else None
                )

        # Generic error extraction
        generic_match = re.search(r"(\w+Error):\s*(.+)", error_output)
        if generic_match:
            return ErrorInfo(
                error_type="generic",
                message=generic_match.group(2)
            )

        return None


class DocumentationFetcher:
    """Fetches relevant documentation based on errors."""

    # Mapping of modules/errors to documentation URLs
    DOC_MAPPINGS = {
        "requests": {
            "base_url": "https://requests.readthedocs.io/en/latest/",
            "topics": {
                "ConnectionError": "user/quickstart/#errors-and-exceptions",
                "Timeout": "user/quickstart/#timeouts",
                "HTTPError": "user/quickstart/#errors-and-exceptions",
                "default": "api/",
            }
        },
        "json": {
            "base_url": "https://docs.python.org/3/library/json.html",
            "topics": {
                "JSONDecodeError": "#json.JSONDecodeError",
                "default": "",
            }
        },
        "os": {
            "base_url": "https://docs.python.org/3/library/os.html",
            "topics": {"default": ""}
        },
        "pathlib": {
            "base_url": "https://docs.python.org/3/library/pathlib.html",
            "topics": {"default": ""}
        },
        "subprocess": {
            "base_url": "https://docs.python.org/3/library/subprocess.html",
            "topics": {
                "CalledProcessError": "#subprocess.CalledProcessError",
                "TimeoutExpired": "#subprocess.TimeoutExpired",
                "default": "",
            }
        },
        "asyncio": {
            "base_url": "https://docs.python.org/3/library/asyncio.html",
            "topics": {"default": ""}
        },
    }

    COMMON_ERRORS_DOC = {
        "import": {
            "title": "Module Import Errors",
            "url": "https://docs.python.org/3/tutorial/modules.html",
            "description": "Guide on Python modules and import system",
            "related": ["pip install", "virtual environments", "PYTHONPATH"]
        },
        "attribute": {
            "title": "Attribute Errors",
            "url": "https://docs.python.org/3/tutorial/classes.html",
            "description": "Understanding Python classes and attributes",
            "related": ["hasattr()", "getattr()", "dir()"]
        },
        "type": {
            "title": "Type Errors",
            "url": "https://docs.python.org/3/library/typing.html",
            "description": "Python type system and type hints",
            "related": ["isinstance()", "type()", "typing module"]
        },
        "syntax": {
            "title": "Syntax Errors",
            "url": "https://docs.python.org/3/tutorial/errors.html",
            "description": "Understanding Python syntax and common mistakes",
            "related": ["indentation", "colons", "parentheses"]
        },
    }

    def get_documentation(self, error_info: ErrorInfo) -> DocReference:
        """Get relevant documentation for an error."""
        log_operation("get_documentation", "STARTED", f"Error type: {error_info.error_type}")

        # Check if we have specific module documentation
        if error_info.module and error_info.module in self.DOC_MAPPINGS:
            mapping = self.DOC_MAPPINGS[error_info.module]
            topic_path = mapping["topics"].get(error_info.error_type, mapping["topics"]["default"])
            url = mapping["base_url"] + topic_path

            return DocReference(
                title=f"{error_info.module} Documentation",
                url=url,
                description=f"Official documentation for {error_info.module} module",
                related_topics=list(mapping["topics"].keys())
            )

        # Fall back to common error documentation
        if error_info.error_type in self.COMMON_ERRORS_DOC:
            doc = self.COMMON_ERRORS_DOC[error_info.error_type]
            return DocReference(
                title=doc["title"],
                url=doc["url"],
                description=doc["description"],
                related_topics=doc["related"]
            )

        # Generic Python documentation
        return DocReference(
            title="Python Documentation",
            url="https://docs.python.org/3/",
            description="Official Python documentation",
            related_topics=["tutorial", "library reference", "language reference"]
        )

    def suggest_fix(self, error_info: ErrorInfo) -> str:
        """Suggest a fix based on the error type."""
        suggestions = {
            "import": f"Try: pip install {error_info.module}\nOr check if the module name is spelled correctly.",
            "attribute": f"The object doesn't have attribute '{error_info.function}'. Check the object type with type() or use dir() to see available attributes.",
            "type": "Check the types of your variables. Use type() to inspect them.",
            "name": f"Variable '{error_info.module}' is not defined. Check for typos or ensure it's defined before use.",
            "value": "The value provided is invalid. Check the expected format/range.",
            "key": f"Key '{error_info.module}' not found. Use .get() method for safe access or check available keys.",
            "index": "List index out of range. Check the list length before accessing.",
            "syntax": "Check for missing colons, parentheses, or incorrect indentation.",
        }

        return suggestions.get(error_info.error_type, "Review the error message and check the documentation.")


class DocAssistant:
    """Main assistant that combines error parsing and documentation fetching."""

    def __init__(self):
        self.parser = ErrorParser()
        self.fetcher = DocumentationFetcher()

    def analyze_error(self, error_output: str) -> dict:
        """Analyze an error and provide documentation and suggestions."""
        error_info = self.parser.parse(error_output)

        if not error_info:
            return {
                "status": "unknown_error",
                "message": "Could not parse the error",
                "suggestion": "Please check the error message manually",
                "doc_url": "https://docs.python.org/3/"
            }

        doc_ref = self.fetcher.get_documentation(error_info)
        suggestion = self.fetcher.suggest_fix(error_info)

        log_operation("analyze_error", "COMPLETED", f"Found docs for {error_info.error_type}")

        return {
            "status": "analyzed",
            "error_type": error_info.error_type,
            "message": error_info.message,
            "suggestion": suggestion,
            "documentation": {
                "title": doc_ref.title,
                "url": doc_ref.url,
                "description": doc_ref.description,
                "related_topics": doc_ref.related_topics
            }
        }

    def print_help(self, error_output: str) -> None:
        """Print formatted help for an error."""
        result = self.analyze_error(error_output)

        print("\n" + "=" * 60)
        print("🔍 ATENA ERROR ANALYSIS")
        print("=" * 60)

        if result["status"] == "unknown_error":
            print(f"\n⚠️  {result['message']}")
        else:
            print(f"\n❌ Error Type: {result['error_type'].upper()}")
            print(f"   Message: {result['message']}")

        print(f"\n💡 Suggestion:")
        print(f"   {result['suggestion']}")

        if "documentation" in result:
            doc = result["documentation"]
            print(f"\n📚 Documentation:")
            print(f"   {doc['title']}")
            print(f"   🔗 {doc['url']}")
            print(f"   {doc['description']}")

            if doc["related_topics"]:
                print(f"\n   Related: {', '.join(doc['related_topics'])}")

        print("\n" + "=" * 60)


if __name__ == "__main__":
    # Example usage
    assistant = DocAssistant()

    test_errors = [
        "ModuleNotFoundError: No module named 'requests'",
        "AttributeError: 'str' object has no attribute 'append'",
        "TypeError: unsupported operand type(s) for +: 'int' and 'str'",
        "KeyError: 'username'",
    ]

    for error in test_errors:
        assistant.print_help(error)
