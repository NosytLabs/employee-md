"""Main validation engine."""

import sys
from pathlib import Path
from typing import Optional

if __package__ is None and __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tooling.validators.base import ValidationResult
from tooling.validators.enums import EnumValidator
from tooling.validators.formats import FormatValidator
from tooling.validators.required import RequiredFieldValidator
from tooling.validators.ranges import RangeValidator
from tooling.validators.types import TypeValidator
from tooling.parser import SecureYAMLParser


class ValidatorEngine:
    """Main validation engine for employee.md files."""

    def __init__(self):
        self.required_validator = RequiredFieldValidator()
        self.enum_validator = EnumValidator()
        self.format_validator = FormatValidator()
        self.range_validator = RangeValidator()
        self.type_validator = TypeValidator()
        self.parser = SecureYAMLParser()

    def validate(
        self, config: dict, file_path: Optional[str] = None
    ) -> ValidationResult:
        """
        Run all validators on config.

        Args:
            config: Parsed YAML config
            file_path: Optional file path for error reporting

        Returns:
            ValidationResult with errors/warnings
        """
        results = []

        results.append(self.validate_required_fields(config))
        results.append(self.validate_enums(config))
        results.append(self.validate_formats(config))
        results.append(self.validate_ranges(config))
        results.append(self.validate_types(config))

        merged = ValidationResult(is_valid=True)
        for result in results:
            merged.errors.extend(result.errors)
            merged.warnings.extend(result.warnings)
            if not result.is_valid:
                merged.is_valid = False

        return merged

    def validate_required_fields(self, config: dict) -> ValidationResult:
        """Validate all required fields."""
        return self.required_validator.validate(config)

    def validate_enums(self, config: dict) -> ValidationResult:
        """Validate enum fields."""
        return self.enum_validator.validate(config)

    def validate_formats(self, config: dict) -> ValidationResult:
        """Validate format fields."""
        return self.format_validator.validate(config)

    def validate_ranges(self, config: dict) -> ValidationResult:
        """Validate range fields."""
        return self.range_validator.validate(config)

    def validate_types(self, config: dict) -> ValidationResult:
        """Validate field types."""
        return self.type_validator.validate(config)


def validate_file(file_path: str) -> ValidationResult:
    """
    Validate a single employee.md file.

    Args:
        file_path: Path to employee.md file

    Returns:
        ValidationResult with errors/warnings
    """
    path = Path(file_path)
    if path.parent.name == "examples" and path.name in {
        "README.md",
        "molt-bot-integration.md",
    }:
        return ValidationResult(is_valid=True)
    try:
        parser = SecureYAMLParser()
        config, _ = parser.parse_file(file_path)
        engine = ValidatorEngine()
        return engine.validate(config, file_path)
    except Exception as e:
        from tooling.validators.base import ValidationError

        return ValidationResult(
            is_valid=False,
            errors=[ValidationError(field="file", message=f"Failed to load file: {e}")],
        )


def validate_files(file_paths: list) -> ValidationResult:
    """
    Validate multiple employee.md files.

    Args:
        file_paths: List of file paths

    Returns:
        Combined ValidationResult
    """
    results = []
    for file_path in file_paths:
        results.append(validate_file(file_path))

    merged = ValidationResult(is_valid=True)
    for result in results:
        merged.errors.extend(result.errors)
        merged.warnings.extend(result.warnings)
        if not result.is_valid:
            merged.is_valid = False

    return merged
