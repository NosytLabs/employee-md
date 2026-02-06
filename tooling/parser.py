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


class DepthLimitExceeded(yaml.MarkedYAMLError):
    """Exception raised when YAML structure exceeds depth limit."""
    pass


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
        # Security: Input path traversal check
        # Check raw input for traversal attempts before resolving
        if ".." in str(filepath).split(os.sep):
            raise YAMLErrorContext(
                f"Path traversal attempt detected: {filepath}", line_number=None
            )

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
                data = yaml.safe_load(f)
        except (IOError, OSError) as e:
            raise YAMLErrorContext(f"Error reading file: {e}", line_number=None)
        except YAMLError as e:
            line_number = self._extract_line_number(e)
            raise YAMLErrorContext(f"YAML parsing error: {e}", line_number=line_number)

        return self._validate_structure(data)

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

        class DepthLimitLoader(yaml.SafeLoader):
            def __init__(self, stream):
                super().__init__(stream)
                self.max_depth = self._outer.max_depth
                self.current_depth = 0

            def compose_mapping_node(self, anchor):
                self.current_depth += 1
                if self.current_depth > self.max_depth:
                    mark = self.peek_event().start_mark
                    raise DepthLimitExceeded(
                        problem=f"YAML nesting too deep: {self.current_depth} levels (max: {self.max_depth})",
                        problem_mark=mark
                    )
                try:
                    return super().compose_mapping_node(anchor)
                finally:
                    self.current_depth -= 1

            def compose_sequence_node(self, anchor):
                self.current_depth += 1
                if self.current_depth > self.max_depth:
                    mark = self.peek_event().start_mark
                    raise DepthLimitExceeded(
                        problem=f"YAML nesting too deep: {self.current_depth} levels (max: {self.max_depth})",
                        problem_mark=mark
                    )
                try:
                    return super().compose_sequence_node(anchor)
                finally:
                    self.current_depth -= 1

        # Attach outer self to loader class
        DepthLimitLoader._outer = self

        try:
            # Use load with DepthLimitLoader to check depth during parsing
            data = yaml.load(content, Loader=DepthLimitLoader)
        except DepthLimitExceeded as e:
            line_number = self._extract_line_number(e)
            # Use e.problem as message
            raise YAMLErrorContext(str(e.problem), line_number=line_number)
        except YAMLError as e:
            line_number = self._extract_line_number(e)
            raise YAMLErrorContext(f"YAML parsing error: {e}", line_number=line_number)

        return self._validate_structure(data)

    def _validate_structure(self, data: Any) -> Tuple[Dict[str, Any], Optional[int]]:
        """Validate structure of parsed YAML data."""
        if data is None:
            return {}, None

        if not isinstance(data, dict):
            raise YAMLErrorContext(
                "Root YAML element must be a dictionary", line_number=None
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
            # Always resolve to canonicalize path and resolve symlinks/..
            resolved_path = path.resolve()

            # Check for path traversal attempts
            str_path = str(resolved_path)
            if ".." in str_path.split(os.sep):
                return False

            # Verify path is within allowed directories
            if self.allowed_directories:
                for allowed_dir in self.allowed_directories:
                    try:
                        resolved_path.relative_to(allowed_dir)
                        return True
                    except ValueError:
                        continue

            return False
        except (ValueError, OSError):
            return False

    def _extract_line_number(self, error: YAMLError) -> Optional[int]:
        """Extract line number from YAML error."""
        if hasattr(error, "problem_mark") and error.problem_mark:
            return error.problem_mark.line + 1
        if hasattr(error, "context_mark") and error.context_mark:
            return error.context_mark.line + 1
        return None
