"""Required field validation."""

from typing import Any, Dict
from .base import BaseValidator, ValidationResult
from ..constants import REQUIRED_SECTIONS, REQUIRED_FIELDS


class RequiredFieldValidator(BaseValidator):
    """Validates that required fields are present."""

    def validate(self, config: Dict[str, Any]) -> ValidationResult:
        self.reset()

        # Check required sections
        for section in REQUIRED_SECTIONS:
            if section not in config:
                self.add_error(
                    field=section, message=f"Missing required section: '{section}'"
                )

        # Check required fields within sections
        for section, fields in REQUIRED_FIELDS.items():
            if section not in config:
                continue

            for field in fields:
                if field not in config[section]:
                    self.add_error(
                        field=f"{section}.{field}",
                        message=f"Missing required field: '{section}.{field}'",
                    )

        return self._create_result()
