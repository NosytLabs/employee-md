"""Tests for BaseValidator and related classes."""

import pytest
from tooling.validators.base import (
    BaseValidator,
    ValidationError,
    ValidationResult,
)


class TestValidationError:
    """Tests for ValidationError dataclass."""

    def test_create_error_with_minimal_fields(self):
        """Test creating ValidationError with minimal required fields."""
        error = ValidationError(field="spec.name", message="Name is required")

        assert error.field == "spec.name"
        assert error.message == "Name is required"
        assert error.severity == "error"
        assert error.line_number is None
        assert error.suggestion is None

    def test_create_error_with_all_fields(self):
        """Test creating ValidationError with all fields."""
        error = ValidationError(
            field="spec.version",
            message="Invalid version format",
            severity="warning",
            line_number=15,
            suggestion="Use semantic versioning (e.g., 1.0.0)",
        )

        assert error.field == "spec.version"
        assert error.message == "Invalid version format"
        assert error.severity == "warning"
        assert error.line_number == 15
        assert error.suggestion == "Use semantic versioning (e.g., 1.0.0)"

    def test_create_error_with_error_severity(self):
        """Test creating ValidationError with error severity."""
        error = ValidationError(field="test", message="Test error", severity="error")

        assert error.severity == "error"

    def test_create_error_with_warning_severity(self):
        """Test creating ValidationError with warning severity."""
        error = ValidationError(
            field="test", message="Test warning", severity="warning"
        )

        assert error.severity == "warning"


class TestValidationResult:
    """Tests for ValidationResult dataclass."""

    def test_create_valid_result(self):
        """Test creating a valid ValidationResult."""
        result = ValidationResult(is_valid=True, errors=[], warnings=[])

        assert result.is_valid is True
        assert result.errors == []
        assert result.warnings == []

    def test_create_invalid_result_with_errors(self):
        """Test creating ValidationResult with errors."""
        errors = [
            ValidationError(field="spec.name", message="Name required"),
            ValidationError(field="spec.version", message="Version required"),
        ]
        result = ValidationResult(is_valid=False, errors=errors, warnings=[])

        assert result.is_valid is False
        assert len(result.errors) == 2
        assert result.errors[0].field == "spec.name"
        assert result.errors[1].field == "spec.version"
        assert result.warnings == []

    def test_create_result_with_warnings_only(self):
        """Test creating ValidationResult with warnings only (still valid)."""
        warnings = [
            ValidationError(
                field="spec.description",
                message="Description is recommended",
                severity="warning",
            )
        ]
        result = ValidationResult(is_valid=True, errors=[], warnings=warnings)

        assert result.is_valid is True
        assert result.errors == []
        assert len(result.warnings) == 1
        assert result.warnings[0].field == "spec.description"

    def test_create_result_with_errors_and_warnings(self):
        """Test creating ValidationResult with both errors and warnings."""
        errors = [ValidationError(field="test", message="Error")]
        warnings = [
            ValidationError(field="test2", message="Warning", severity="warning")
        ]

        result = ValidationResult(is_valid=False, errors=errors, warnings=warnings)

        assert result.is_valid is False
        assert len(result.errors) == 1
        assert len(result.warnings) == 1


class TestBaseValidator:
    """Tests for BaseValidator abstract class."""

    def test_base_validator_has_errors_list(self):
        """Test that BaseValidator initializes with empty errors list."""
        validator = MockValidator()
        assert validator.errors == []

    def test_base_validator_has_warnings_list(self):
        """Test that BaseValidator initializes with empty warnings list."""
        validator = MockValidator()
        assert validator.warnings == []

    def test_add_error_creates_error(self):
        """Test adding an error to the validator."""
        validator = MockValidator()
        validator.add_error("spec.name", "Name is required")

        assert len(validator.errors) == 1
        assert validator.errors[0].field == "spec.name"
        assert validator.errors[0].message == "Name is required"
        assert validator.errors[0].severity == "error"

    def test_add_error_with_line_number(self):
        """Test adding an error with line number."""
        validator = MockValidator()
        validator.add_error("spec.version", "Invalid version", line_number=42)

        assert validator.errors[0].line_number == 42

    def test_add_error_with_suggestion(self):
        """Test adding an error with suggestion."""
        validator = MockValidator()
        validator.add_error(
            "spec.version", "Invalid version", suggestion="Use semantic versioning"
        )

        assert validator.errors[0].suggestion == "Use semantic versioning"

    def test_add_warning_creates_warning(self):
        """Test adding a warning to the validator."""
        validator = MockValidator()
        validator.add_warning("spec.description", "Description is recommended")

        assert len(validator.warnings) == 1
        assert validator.warnings[0].field == "spec.description"
        assert validator.warnings[0].message == "Description is recommended"
        assert validator.warnings[0].severity == "warning"

    def test_add_warning_with_line_number(self):
        """Test adding a warning with line number."""
        validator = MockValidator()
        validator.add_warning("spec.description", "Warning", line_number=15)

        assert validator.warnings[0].line_number == 15

    def test_add_multiple_errors(self):
        """Test adding multiple errors."""
        validator = MockValidator()
        validator.add_error("field1", "Error 1")
        validator.add_error("field2", "Error 2")
        validator.add_error("field3", "Error 3")

        assert len(validator.errors) == 3
        assert validator.errors[0].field == "field1"
        assert validator.errors[1].field == "field2"
        assert validator.errors[2].field == "field3"

    def test_add_multiple_warnings(self):
        """Test adding multiple warnings."""
        validator = MockValidator()
        validator.add_warning("field1", "Warning 1")
        validator.add_warning("field2", "Warning 2")

        assert len(validator.warnings) == 2
        assert validator.warnings[0].field == "field1"
        assert validator.warnings[1].field == "field2"

    def test_reset_clears_errors_and_warnings(self):
        """Test that reset clears errors and warnings."""
        validator = MockValidator()
        validator.add_error("field1", "Error")
        validator.add_warning("field2", "Warning")

        assert len(validator.errors) == 1
        assert len(validator.warnings) == 1

        validator.reset()

        assert len(validator.errors) == 0
        assert len(validator.warnings) == 0

    def test_create_result_with_no_errors(self):
        """Test _create_result with no errors."""
        validator = MockValidator()
        result = validator._create_result()

        assert result.is_valid is True
        assert result.errors == []
        assert result.warnings == []

    def test_create_result_with_errors(self):
        """Test _create_result with errors."""
        validator = MockValidator()
        validator.add_error("field1", "Error 1")
        validator.add_error("field2", "Error 2")

        result = validator._create_result()

        assert result.is_valid is False
        assert len(result.errors) == 2
        assert result.warnings == []

    def test_create_result_with_warnings(self):
        """Test _create_result with warnings."""
        validator = MockValidator()
        validator.add_warning("field1", "Warning 1")
        validator.add_warning("field2", "Warning 2")

        result = validator._create_result()

        assert result.is_valid is True
        assert result.errors == []
        assert len(result.warnings) == 2

    def test_create_result_with_errors_and_warnings(self):
        """Test _create_result with both errors and warnings."""
        validator = MockValidator()
        validator.add_error("field1", "Error")
        validator.add_warning("field2", "Warning")

        result = validator._create_result()

        assert result.is_valid is False
        assert len(result.errors) == 1
        assert len(result.warnings) == 1


class MockValidator(BaseValidator):
    """Mock validator for testing BaseValidator."""

    def validate(self, data: dict) -> ValidationResult:
        """Mock validate method."""
        return self._create_result()
