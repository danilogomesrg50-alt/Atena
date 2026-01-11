"""
ATENA Framework - Configuration Module
Central configuration for the automation framework.
"""
import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent
CORE_DIR = BASE_DIR / "core"
MODULES_DIR = BASE_DIR / "modules"
LOGS_DIR = BASE_DIR / "logs"

# Ensure directories exist
for directory in [CORE_DIR, MODULES_DIR, LOGS_DIR]:
    directory.mkdir(exist_ok=True)

# Logging configuration
LOG_FILE = LOGS_DIR / "atena.log"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_LEVEL = os.getenv("ATENA_LOG_LEVEL", "INFO")

# Code analysis settings
CODE_EXTENSIONS = [".py", ".js", ".ts", ".java", ".cpp", ".c"]
MAX_FUNCTION_LENGTH = 50  # lines
MAX_COMPLEXITY = 10  # cyclomatic complexity threshold

# API documentation sources
DOC_SOURCES = {
    "python": "https://docs.python.org/3/",
    "requests": "https://requests.readthedocs.io/",
    "flask": "https://flask.palletsprojects.com/",
    "django": "https://docs.djangoproject.com/",
}
