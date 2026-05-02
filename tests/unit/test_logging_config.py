"""Tests for logging configuration."""

import pytest
import logging
import io
from contextlib import redirect_stderr, redirect_stdout
from tooling.logging_config import (
    get_logger,
    ValidatorLogger,
    reset_logger,
)


class TestValidatorLogger:
    """Tests for ValidatorLogger class."""

    def test_logger_creation(self):
        """Test creating a logger."""
        logger = ValidatorLogger("test_logger")

        assert logger.name == "test_logger"
        assert isinstance(logger.logger, logging.Logger)

    def test_logger_singleton_same_name(self):
        """Test that loggers with same name are same instance."""
        reset_logger()
        logger1 = ValidatorLogger("test_singleton")
        logger2 = ValidatorLogger("test_singleton")

        assert logger1 is logger2

    def test_logger_different_name(self):
        """Test that loggers with different names are different instances."""
        reset_logger()
        logger1 = ValidatorLogger("logger1")
        logger2 = ValidatorLogger("logger2")

        assert logger1 is not logger2

    def test_info_level(self):
        """Test setting info log level."""
        reset_logger()
        logger = ValidatorLogger("test_info")
        logger.set_level(logging.INFO)

        assert logger.logger.level == logging.INFO

    def test_debug_level(self):
        """Test setting debug log level."""
        reset_logger()
        logger = ValidatorLogger("test_debug")
        logger.set_level(logging.DEBUG)

        assert logger.logger.level == logging.DEBUG

    def test_error_level(self):
        """Test setting error log level."""
        reset_logger()
        logger = ValidatorLogger("test_error")
        logger.set_level(logging.ERROR)

        assert logger.logger.level == logging.ERROR

    def test_logging_methods(self):
        """Test that logging methods work correctly."""
        reset_logger()
        logger = ValidatorLogger("test_methods")

        # Test all logging methods
        logger.debug("Debug message", field="test_field")
        logger.info("Info message", field="test_field")
        logger.warning("Warning message", field="test_field")
        logger.error("Error message", field="test_field")

    def test_logging_with_context(self):
        """Test logging with context dictionary."""
        reset_logger()
        logger = ValidatorLogger("test_context")

        logger.info(
            "Message with context",
            field="spec.name",
            validator="TestValidator",
            value="test_value",
        )

    def test_logging_without_context(self):
        """Test logging without context."""
        reset_logger()
        logger = ValidatorLogger("test_no_context")

        logger.info("Simple message")
        logger.warning("Warning")
        logger.error("Error")


class TestGetLogger:
    """Tests for get_logger function."""

    def test_get_logger_returns_validator_logger(self):
        """Test that get_logger returns ValidatorLogger instance."""
        reset_logger()
        logger = get_logger("test_get_logger")

        assert isinstance(logger, ValidatorLogger)

    def test_get_logger_same_instance(self):
        """Test that get_logger returns same instance for same name."""
        reset_logger()
        logger1 = get_logger("test_same")
        logger2 = get_logger("test_same")

        assert logger1 is logger2

    def test_get_logger_default_level(self):
        """Test that get_logger sets default level."""
        reset_logger()
        logger = get_logger("test_default_level")

        assert logger.logger.level == logging.INFO


class TestResetLogger:
    """Tests for reset_logger function."""

    def test_reset_logger_clears_handlers(self):
        """Test that reset_logger clears handlers."""
        reset_logger()
        logger = get_logger("test_reset")
        initial_count = len(logger.logger.handlers)

        reset_logger()

        assert len(logger.logger.handlers) < initial_count

    def test_reset_logger_reinitializes(self):
        """Test that reset_logger reinitializes logger."""
        reset_logger()
        logger1 = get_logger("test_reinit")
        logger1.set_level(logging.DEBUG)

        reset_logger()
        logger2 = get_logger("test_reinit")

        assert logger2 is not logger1
