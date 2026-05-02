"""Type validation."""

from typing import Any, Dict
from .base import BaseValidator, ValidationResult
from ..constants import VALIDATION_RULES
from ..utils import check_type


class TypeValidator(BaseValidator):
    """Validates field types."""

    def validate(self, config: Dict[str, Any]) -> ValidationResult:
        self.reset()

        for section in config.keys() & VALIDATION_RULES.keys():
            fields = VALIDATION_RULES[section]
            section_data = config[section]

            if isinstance(fields, list):
                if not isinstance(section_data, list):
                    self.add_error(
                        field=section,
                        message=f"Invalid type for {section}: expected list, got {type(section_data).__name__}",
                    )
                continue

            if not isinstance(fields, dict):
                continue

            if not isinstance(section_data, dict):
                self.add_error(
                    field=section,
                    message=f"Invalid type for {section}: expected dict, got {type(section_data).__name__}",
                )
                continue

            for field in section_data.keys() & fields.keys():
                expected_type = fields[field]
                value = section_data[field]

                if not check_type(value, expected_type):
                    type_name = self._get_type_name(expected_type)
                    self.add_error(
                        field=f"{section}.{field}",
                        message=f"Invalid type for {section}.{field}: expected {type_name}, got {type(value).__name__}",
                    )

        return self._create_result()

    def _get_type_name(self, expected_type: Any) -> str:
        if isinstance(expected_type, tuple):
            return " | ".join(t.__name__ for t in expected_type)
        return expected_type.__name__
