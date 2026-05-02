
import os
import pytest
from pathlib import Path
from tooling.parser import SecureYAMLParser

class TestSecurity:
    """Security tests for parser."""

    def test_symlink_bypass_prevention(self, tmp_path):
        """Test that _is_safe_path prevents symlink traversal."""
        # Setup: safe dir and secret file outside
        safe_dir = tmp_path / "safe"
        safe_dir.mkdir()

        secret_file = tmp_path / "secret.yaml"
        secret_file.write_text("secret: true")

        # Create a symlink in safe_dir pointing to secret_file
        symlink_path = safe_dir / "link_to_secret.yaml"
        os.symlink(secret_file, symlink_path)

        # Initialize parser allowing only safe_dir
        parser = SecureYAMLParser(allowed_directories=[str(safe_dir)])

        # Checking the symlink path.
        # Crucial: we pass it as an absolute path, because that's what triggered the bug.
        # tmp_path is already absolute.
        abs_symlink_path = symlink_path.absolute()

        # Verify setup
        assert abs_symlink_path.is_absolute()
        assert abs_symlink_path.is_symlink()
        assert str(safe_dir) in str(abs_symlink_path)

        # This check should fail (return False) because it resolves to secret_file
        # which is NOT in safe_dir.
        is_safe = parser._is_safe_path(abs_symlink_path)

        assert is_safe is False, "Symlink traversal should be detected and blocked"
