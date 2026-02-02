"""Numeric range validation."""

from typing import Any, Dict
from .base import BaseValidator, ValidationResult
from ..constants import RANGE_CONSTRAINTS
from ..utils import get_nested_value


class RangeValidator(BaseValidator):
    """Validates numeric ranges."""

    def validate(self, config: Dict[str, Any]) -> ValidationResult:
        self.reset()

        for field_path, (min_val, max_val) in RANGE_CONSTRAINTS.items():
            value = get_nested_value(config, field_path)

            if value is None:
                continue

            if not isinstance(value, (int, float)):
                continue

            if not (min_val <= value <= max_val):
                self.add_error(
                    field=field_path,
                    message=f"Invalid {field_path}: {value}. Must be between {min_val} and {max_val}",
                )

        return self._create_result()
