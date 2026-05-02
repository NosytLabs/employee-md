"""Base validator class."""

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

_production_mode: bool = False


def set_production_mode(enabled: bool) -> None:
    """Set production mode for error message sanitization."""
    global _production_mode
    _production_mode = enabled


def get_production_mode() -> bool:
    """Get current production mode status."""
    return _production_mode


# Compiled regexes for sanitization
_WINDOWS_PATH_REGEX = re.compile(r"[A-Z]:\\[^\\]+\\[^\\]+")
_UNIX_PATH_REGEX = re.compile(r"/[^/\s]+/[^/\s]+")
_ETH_WALLET_REGEX = re.compile(r"0x[a-fA-F0-9]{40}")
_BTC_WALLET_REGEX = re.compile(r"\b[13][a-km-zA-HJ-NP-Z1-9]{25,39}\b")


def _sanitize_path_in_message(message: str) -> str:
    """Remove file system paths from error messages in production mode."""
    if not _production_mode:
        return message

    # Remove Windows paths like C:\path\to\file
    message = _WINDOWS_PATH_REGEX.sub("[REDACTED_PATH]", message)
    # Remove Unix paths like /path/to/file
    message = _UNIX_PATH_REGEX.sub("[REDACTED_PATH]", message)

    return message


def _sanitize_wallet_in_message(message: str) -> str:
    """Remove wallet addresses from error messages in production mode."""
    if not _production_mode:
        return message

    # Ethereum addresses: 0x + 40 hex chars
    message = _ETH_WALLET_REGEX.sub("0x[REDACTED]", message)
    # Bitcoin-style addresses: 26-42 chars
    message = _BTC_WALLET_REGEX.sub("[REDACTED_WALLET]", message)

    return message


@dataclass
class ValidationError:
    """Represents a single validation error."""

    field: str
    message: str
    severity: str = "error"
    line_number: Optional[int] = None
    suggestion: Optional[str] = None

    def get_sanitized_message(self) -> str:
        """Get sanitized error message (in production mode)."""
        message = _sanitize_path_in_message(self.message)
        message = _sanitize_wallet_in_message(message)
        return message

    def get_formatted_error(self) -> str:
        """Get formatted error message with suggestion if available."""
        error_msg = f"{self.field}: {self.get_sanitized_message()}"
        if self.suggestion:
            error_msg += f"\n  Suggestion: {self.suggestion}"
        return error_msg


@dataclass
class ValidationResult:
    """Result of validation."""

    is_valid: bool
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationError] = field(default_factory=list)

    @property
    def error_count(self) -> int:
        return len(self.errors)

    @property
    def warning_count(self) -> int:
        return len(self.warnings)


class BaseValidator(ABC):
    """Abstract base class for all validators."""

    def __init__(self):
        self.errors: List[ValidationError] = []
        self.warnings: List[ValidationError] = []

    @abstractmethod
    def validate(self, config: Dict[str, Any]) -> ValidationResult:
        """Validate configuration."""
        pass

    def add_error(
        self,
        field: str,
        message: str,
        line_number: Optional[int] = None,
        suggestion: Optional[str] = None,
    ):
        """Add an error to result."""
        self.errors.append(
            ValidationError(
                field=field,
                message=message,
                severity="error",
                line_number=line_number,
                suggestion=suggestion,
            )
        )

    def add_warning(
        self,
        field: str,
        message: str,
        line_number: Optional[int] = None,
        suggestion: Optional[str] = None,
    ):
        """Add a warning to result."""
        self.warnings.append(
            ValidationError(
                field=field,
                message=message,
                severity="warning",
                line_number=line_number,
                suggestion=suggestion,
            )
        )

    def _create_result(self) -> ValidationResult:
        """Create ValidationResult from current errors and warnings."""
        return ValidationResult(
            is_valid=len(self.errors) == 0, errors=self.errors, warnings=self.warnings
        )

    def reset(self):
        """Reset errors and warnings."""
        self.errors = []
        self.warnings = []
