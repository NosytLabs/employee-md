"""Structured logging infrastructure for employee.md validator."""

import logging
import sys
from typing import Any, Dict, Optional


class ValidatorLogger:
    """Structured logger for validation operations."""

    _instances: Dict[str, "ValidatorLogger"] = {}

    def __new__(
        cls,
        name: str = "employee_validator",
        level: int = logging.INFO,
        log_format: Optional[str] = None,
    ) -> "ValidatorLogger":
        """Create or return existing logger instance (singleton per name)."""
        if name in cls._instances:
            return cls._instances[name]

        instance = super().__new__(cls)
        cls._instances[name] = instance
        return instance

    def __init__(
        self,
        name: str = "employee_validator",
        level: int = logging.INFO,
        log_format: Optional[str] = None,
    ) -> None:
        """
        Initialize validator logger.

        Args:
            name: Logger name
            level: Logging level (DEBUG, INFO, WARNING, ERROR)
            log_format: Optional custom log format
        """
        if hasattr(self, "_initialized"):
            return

        self._initialized = True
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Remove existing handlers
        self.logger.handlers.clear()

        # Create console handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)

        # Set format
        if log_format is None:
            log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        formatter = logging.Formatter(log_format)
        handler.setFormatter(formatter)

        self.logger.addHandler(handler)

    def set_level(self, level: int) -> None:
        """Set logging level."""
        self.logger.setLevel(level)
        for handler in self.logger.handlers:
            handler.setLevel(level)

    def debug(self, message: str, **context: Any) -> None:
        """Log debug message with optional context."""
        if context:
            message = self._format_with_context(message, context)
        self.logger.debug(message)

    def info(self, message: str, **context: Any) -> None:
        """Log info message with optional context."""
        if context:
            message = self._format_with_context(message, context)
        self.logger.info(message)

    def warning(self, message: str, **context: Any) -> None:
        """Log warning message with optional context."""
        if context:
            message = self._format_with_context(message, context)
        self.logger.warning(message)

    def error(self, message: str, **context: Any) -> None:
        """Log error message with optional context."""
        if context:
            message = self._format_with_context(message, context)
        self.logger.error(message)

    def _format_with_context(self, message: str, context: Dict[str, Any]) -> str:
        """Format message with context dictionary."""
        context_str = ", ".join(f"{k}={v}" for k, v in context.items())
        return f"{message} | {context_str}"


def get_logger(
    name: str = "employee_validator", level: int = logging.INFO
) -> ValidatorLogger:
    """
    Get or create a validator logger instance.

    Args:
        name: Logger name
        level: Logging level

    Returns:
        ValidatorLogger instance
    """
    if name not in ValidatorLogger._instances:
        ValidatorLogger._instances[name] = ValidatorLogger(name=name, level=level)
    return ValidatorLogger._instances[name]


def reset_logger() -> None:
    """Reset all logger instances."""
    for instance in ValidatorLogger._instances.values():
        instance.logger.handlers.clear()
    ValidatorLogger._instances.clear()
