#!/usr/bin/env python3
"""
ATENA Framework - Main Entry Point
Continuous execution bot for Render/Railway deployment.
"""
import os
import sys
import time
import signal
import threading
from datetime import datetime
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.logger import setup_logger, log_operation
from core.config import BASE_DIR, LOGS_DIR
from modules.code_analyzer import CodeAnalyzer
from modules.doc_fetcher import DocAssistant

logger = setup_logger("atena_bot")

# Configuration from environment
PORT = int(os.getenv("PORT", 8080))
HEALTH_CHECK_INTERVAL = int(os.getenv("HEALTH_CHECK_INTERVAL", 60))
BOT_NAME = os.getenv("BOT_NAME", "ATENA")


class AtenaBot:
    """Main bot class for continuous execution."""

    def __init__(self):
        self.running = False
        self.start_time = None
        self.task_count = 0
        self.analyzer = CodeAnalyzer()
        self.doc_assistant = DocAssistant()
        self.status = "initialized"

    def start(self):
        """Start the bot."""
        self.running = True
        self.start_time = datetime.now()
        self.status = "running"
        log_operation("bot_start", "SUCCESS", f"{BOT_NAME} started at {self.start_time}")
        logger.info(f"🤖 {BOT_NAME} Bot started successfully")

    def stop(self):
        """Stop the bot gracefully."""
        self.running = False
        self.status = "stopped"
        log_operation("bot_stop", "SUCCESS", f"{BOT_NAME} stopped")
        logger.info(f"🛑 {BOT_NAME} Bot stopped")

    def get_uptime(self) -> str:
        """Get bot uptime as formatted string."""
        if not self.start_time:
            return "Not started"
        delta = datetime.now() - self.start_time
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours}h {minutes}m {seconds}s"

    def get_status(self) -> dict:
        """Get current bot status."""
        return {
            "name": BOT_NAME,
            "status": self.status,
            "uptime": self.get_uptime(),
            "tasks_processed": self.task_count,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "current_time": datetime.now().isoformat(),
            "version": "1.0.0"
        }

    def analyze_project(self, path: str = ".") -> dict:
        """Run code analysis on a path."""
        self.task_count += 1
        log_operation("analyze_project", "STARTED", path)

        results = self.analyzer.analyze_path(path)
        total_issues = sum(len(r.issues) for r in results)

        summary = {
            "files_analyzed": len(results),
            "total_issues": total_issues,
            "issues_by_severity": {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
        }

        for result in results:
            for issue in result.issues:
                summary["issues_by_severity"][issue.severity] += 1

        log_operation("analyze_project", "COMPLETED", f"{total_issues} issues found")
        return summary

    def get_error_help(self, error_message: str) -> dict:
        """Get help for an error message."""
        self.task_count += 1
        return self.doc_assistant.analyze_error(error_message)

    def heartbeat(self):
        """Periodic heartbeat for health monitoring."""
        while self.running:
            logger.debug(f"💓 Heartbeat - Uptime: {self.get_uptime()}")
            time.sleep(HEALTH_CHECK_INTERVAL)


# Global bot instance
bot = AtenaBot()


class HealthHandler(BaseHTTPRequestHandler):
    """HTTP handler for health checks and API endpoints."""

    def log_message(self, format, *args):
        """Override to use our logger."""
        logger.debug(f"HTTP: {args[0]}")

    def _send_json(self, data: dict, status: int = 200):
        """Send JSON response."""
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())

    def do_GET(self):
        """Handle GET requests."""
        if self.path == "/" or self.path == "/health":
            self._send_json({
                "status": "healthy",
                "bot": bot.get_status()
            })

        elif self.path == "/status":
            self._send_json(bot.get_status())

        elif self.path == "/analyze":
            result = bot.analyze_project(".")
            self._send_json(result)

        elif self.path.startswith("/analyze/"):
            path = self.path[9:]  # Remove "/analyze/"
            result = bot.analyze_project(path)
            self._send_json(result)

        elif self.path == "/logs":
            log_file = LOGS_DIR / "atena.log"
            if log_file.exists():
                lines = log_file.read_text().split("\n")[-50:]  # Last 50 lines
                self._send_json({"logs": lines})
            else:
                self._send_json({"logs": []})

        else:
            self._send_json({"error": "Not found"}, 404)

    def do_POST(self):
        """Handle POST requests."""
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode() if content_length > 0 else "{}"

        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            self._send_json({"error": "Invalid JSON"}, 400)
            return

        if self.path == "/error-help":
            error_msg = data.get("error", "")
            if not error_msg:
                self._send_json({"error": "Missing 'error' field"}, 400)
                return
            result = bot.get_error_help(error_msg)
            self._send_json(result)

        elif self.path == "/analyze":
            path = data.get("path", ".")
            result = bot.analyze_project(path)
            self._send_json(result)

        else:
            self._send_json({"error": "Not found"}, 404)


def run_server():
    """Run the HTTP server."""
    server = HTTPServer(("0.0.0.0", PORT), HealthHandler)
    logger.info(f"🌐 HTTP server running on port {PORT}")
    server.serve_forever()


def signal_handler(signum, frame):
    """Handle shutdown signals."""
    logger.info(f"Received signal {signum}, shutting down...")
    bot.stop()
    sys.exit(0)


def main():
    """Main entry point."""
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print(f"""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║     █████╗ ████████╗███████╗███╗   ██╗ █████╗            ║
║    ██╔══██╗╚══██╔══╝██╔════╝████╗  ██║██╔══██╗           ║
║    ███████║   ██║   █████╗  ██╔██╗ ██║███████║           ║
║    ██╔══██║   ██║   ██╔══╝  ██║╚██╗██║██╔══██║           ║
║    ██║  ██║   ██║   ███████╗██║ ╚████║██║  ██║           ║
║    ╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═══╝╚═╝  ╚═╝           ║
║                                                          ║
║    Automated Task Environment for Networked Automation   ║
║                        v1.0.0                            ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
    """)

    # Start the bot
    bot.start()

    # Start heartbeat thread
    heartbeat_thread = threading.Thread(target=bot.heartbeat, daemon=True)
    heartbeat_thread.start()

    # Run HTTP server (blocking)
    logger.info(f"🚀 {BOT_NAME} is ready!")
    logger.info(f"📡 Endpoints available:")
    logger.info(f"   GET  /health  - Health check")
    logger.info(f"   GET  /status  - Bot status")
    logger.info(f"   GET  /analyze - Analyze current project")
    logger.info(f"   GET  /logs    - View recent logs")
    logger.info(f"   POST /error-help - Get help for errors")

    try:
        run_server()
    except KeyboardInterrupt:
        bot.stop()


if __name__ == "__main__":
    main()
