#!/usr/bin/env python3
"""
ATENA Framework - Task Manager
Main entry point for managing development tasks, dependencies, and automation.
"""
import subprocess
import sys
from pathlib import Path
from typing import Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.logger import setup_logger, log_operation, log_error
from core.config import BASE_DIR

logger = setup_logger("manager")


class DependencyManager:
    """Manages project dependencies installation and updates."""

    def __init__(self, requirements_file: str = "requirements.txt"):
        self.requirements_path = BASE_DIR / requirements_file

    def install_dependencies(self, upgrade: bool = False) -> bool:
        """Install all dependencies from requirements.txt."""
        if not self.requirements_path.exists():
            log_error("install_dependencies", FileNotFoundError(
                f"Requirements file not found: {self.requirements_path}"
            ))
            return False

        cmd = [sys.executable, "-m", "pip", "install", "-r", str(self.requirements_path)]
        if upgrade:
            cmd.append("--upgrade")

        log_operation("install_dependencies", "STARTED", str(self.requirements_path))

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            log_operation("install_dependencies", "SUCCESS", f"Installed from {self.requirements_path}")
            return True
        except subprocess.CalledProcessError as e:
            log_error("install_dependencies", e)
            print(f"Error output: {e.stderr}")
            return False

    def install_package(self, package: str) -> bool:
        """Install a single package."""
        cmd = [sys.executable, "-m", "pip", "install", package]
        log_operation("install_package", "STARTED", package)

        try:
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            log_operation("install_package", "SUCCESS", package)
            return True
        except subprocess.CalledProcessError as e:
            log_error("install_package", e)
            return False

    def list_installed(self) -> list[str]:
        """List all installed packages."""
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list", "--format=freeze"],
            capture_output=True,
            text=True
        )
        return result.stdout.strip().split("\n")


class CommandExecutor:
    """Executes shell commands with logging and error handling."""

    @staticmethod
    def run(command: str, cwd: Optional[Path] = None, timeout: int = 300) -> tuple[bool, str, str]:
        """
        Execute a shell command.
        Returns: (success, stdout, stderr)
        """
        log_operation("command_execute", "STARTED", command)

        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd or BASE_DIR,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            success = result.returncode == 0
            status = "SUCCESS" if success else "FAILED"
            log_operation("command_execute", status, f"Exit code: {result.returncode}")
            return success, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            log_error("command_execute", TimeoutError(f"Command timed out: {command}"))
            return False, "", "Command timed out"
        except Exception as e:
            log_error("command_execute", e)
            return False, "", str(e)


def main():
    """Main entry point for CLI usage."""
    import argparse

    parser = argparse.ArgumentParser(
        description="ATENA Framework - Development Task Manager"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Install command
    install_parser = subparsers.add_parser("install", help="Install dependencies")
    install_parser.add_argument("--upgrade", "-u", action="store_true", help="Upgrade packages")
    install_parser.add_argument("--package", "-p", type=str, help="Install specific package")

    # Run command
    run_parser = subparsers.add_parser("run", help="Execute a shell command")
    run_parser.add_argument("cmd", type=str, help="Command to execute")

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze code for improvements")
    analyze_parser.add_argument("path", type=str, nargs="?", default=".", help="Path to analyze")

    args = parser.parse_args()

    if args.command == "install":
        dm = DependencyManager()
        if args.package:
            success = dm.install_package(args.package)
        else:
            success = dm.install_dependencies(upgrade=args.upgrade)
        sys.exit(0 if success else 1)

    elif args.command == "run":
        executor = CommandExecutor()
        success, stdout, stderr = executor.run(args.cmd)
        if stdout:
            print(stdout)
        if stderr:
            print(stderr, file=sys.stderr)
        sys.exit(0 if success else 1)

    elif args.command == "analyze":
        # Import here to avoid circular imports
        from modules.code_analyzer import CodeAnalyzer
        analyzer = CodeAnalyzer()
        results = analyzer.analyze_path(args.path)
        analyzer.print_report(results)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
