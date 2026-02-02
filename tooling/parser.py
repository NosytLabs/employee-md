"""Secure YAML parser with resource limits and error context."""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
import yaml
from yaml import YAMLError

from .constants import MAX_YAML_DEPTH, MAX_FILE_SIZE


class YAMLErrorContext(Exception):
    """Exception with YAML line number context."""

    def __init__(self, message: str, line_number: Optional[int] = None):
        self.line_number = line_number
        super().__init__(message)


class SecureYAMLParser:
    """YAML parser with security hardening."""

    def __init__(
        self,
        max_depth: int = MAX_YAML_DEPTH,
        max_size: int = MAX_FILE_SIZE,
        allowed_directories: Optional[List[str]] = None,
    ):
        self.max_depth = max_depth
        self.max_size = max_size
        self.allowed_directories = self._normalize_allowed_dirs(allowed_directories)

    def parse_file(self, filepath: str) -> Tuple[Dict[str, Any], Optional[int]]:
        """Parse a YAML file with security checks.

        Args:
            filepath: Path to YAML file

        Returns:
            Tuple of (parsed_data, error_line_number)

        Raises:
            YAMLErrorContext: If parsing fails or security checks fail
        """
        # Security: Path traversal protection
        resolved_path = Path(filepath).resolve()
        if not self._is_safe_path(resolved_path):
            raise YAMLErrorContext(
                f"Path traversal attempt detected: {filepath}", line_number=None
            )

        # Security: File existence check
        if not resolved_path.exists():
            raise YAMLErrorContext(f"File not found: {filepath}", line_number=None)

        # Security: File size limit
        file_size = resolved_path.stat().st_size
        if file_size > self.max_size:
            raise YAMLErrorContext(
                f"File too large: {file_size} bytes (max: {self.max_size})",
                line_number=None,
            )

        try:
            with open(resolved_path, "r", encoding="utf-8") as f:
                content = f.read()
        except (IOError, OSError) as e:
            raise YAMLErrorContext(f"Error reading file: {e}", line_number=None)

        return self.parse_string(content)

    def parse_string(self, content: str) -> Tuple[Dict[str, Any], Optional[int]]:
        """Parse YAML content from string.

        Args:
            content: YAML content as string

        Returns:
            Tuple of (parsed_data, error_line_number)

        Raises:
            YAMLErrorContext: If parsing fails or security checks fail
        """
        # Security: Content size limit
        if len(content.encode("utf-8")) > self.max_size:
            raise YAMLErrorContext(
                f"Content too large: {len(content)} bytes (max: {self.max_size})",
                line_number=None,
            )

        try:
            # Use safe_load to prevent arbitrary code execution
            data = yaml.safe_load(content)
        except YAMLError as e:
            line_number = self._extract_line_number(e)
            raise YAMLErrorContext(f"YAML parsing error: {e}", line_number=line_number)

        if data is None:
            return {}, None

        if not isinstance(data, dict):
            raise YAMLErrorContext(
                "Root YAML element must be a dictionary", line_number=None
            )

        # Security: Depth limit check
        depth = self._calculate_depth(data)
        if depth > self.max_depth:
            raise YAMLErrorContext(
                f"YAML nesting too deep: {depth} levels (max: {self.max_depth})",
                line_number=None,
            )

        return data, None

    def _normalize_allowed_dirs(self, directories: Optional[List[str]]) -> Set[Path]:
        """Normalize and resolve allowed directories to absolute paths."""
        if directories is None:
            return set()

        normalized = set()
        for directory in directories:
            try:
                abs_path = Path(directory).resolve()
                normalized.add(abs_path)
            except (ValueError, OSError):
                continue
        return normalized

    def _is_safe_path(self, path: Path) -> bool:
        """Check if path is safe (no traversal outside allowed dirs)."""
        # Normalize and check for traversal
        try:
            resolved_path = path.resolve()

            # Check for path traversal attempts
            str_path = str(resolved_path)
            if ".." in str_path.split(os.sep):
                return False

            # If allowlist is configured, verify path is within allowed directories
            if self.allowed_directories:
                for allowed_dir in self.allowed_directories:
                    try:
                        resolved_path.relative_to(allowed_dir)
                        return True
                    except ValueError:
                        continue
                return False

            return True
        except (ValueError, OSError):
            return False

    def _calculate_depth(self, obj: Any, current_depth: int = 0) -> int:
        """Calculate maximum nesting depth of a data structure.

        Optimized with early termination to prevent unnecessary traversal of deep structures.

        Args:
            obj: The data structure to calculate depth for
            current_depth: Current depth in traversal

        Returns:
            Maximum depth of the structure
        """
        if current_depth > self.max_depth:
            return current_depth

        if isinstance(obj, dict):
            if not obj:
                return current_depth

            max_child_depth = current_depth
            for v in obj.values():
                child_depth = self._calculate_depth(v, current_depth + 1)
                if child_depth > max_child_depth:
                    max_child_depth = child_depth
                    if max_child_depth > self.max_depth:
                        return max_child_depth
            return max_child_depth

        elif isinstance(obj, list):
            if not obj:
                return current_depth

            max_child_depth = current_depth
            for item in obj:
                child_depth = self._calculate_depth(item, current_depth + 1)
                if child_depth > max_child_depth:
                    max_child_depth = child_depth
                    if max_child_depth > self.max_depth:
                        return max_child_depth
            return max_child_depth

        else:
            return current_depth

    def _extract_line_number(self, error: YAMLError) -> Optional[int]:
        """Extract line number from YAML error."""
        if hasattr(error, "problem_mark") and error.problem_mark:
            return error.problem_mark.line + 1
        if hasattr(error, "context_mark") and error.context_mark:
            return error.context_mark.line + 1
        return None
