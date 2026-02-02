"""Integration tests for CLI."""

import subprocess
import sys
from pathlib import Path


class TestCLI:
    """Test CLI interface."""

    def test_cli_help(self):
        """Test CLI help output."""
        result = subprocess.run(
            [sys.executable, "-m", "tooling.cli", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "Validate employee.md" in result.stdout
        assert "--format" in result.stdout
        assert "--parallel" in result.stdout
        assert "--production" in result.stdout

    def test_cli_version(self):
        """Test CLI version output."""
        result = subprocess.run(
            [sys.executable, "-m", "tooling.cli", "--version"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "2.1.0" in result.stdout

    def test_cli_clear_cache(self):
        """Test cache clearing."""
        result = subprocess.run(
            [sys.executable, "-m", "tooling.cli", "--clear-cache"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "Cache cleared" in result.stdout

    def test_cli_invalid_file(self):
        """Test handling of invalid file."""
        result = subprocess.run(
            [sys.executable, "-m", "tooling.cli", "nonexistent.md"],
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0
        assert "No files found" in result.stderr or "Error" in result.stderr
