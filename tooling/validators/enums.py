"""Enum validation."""

from typing import Any, Dict
from .base import BaseValidator, ValidationResult, ValidationError
from ..constants import LEVEL_ENUM, STATUS_ENUM, SPEC_STATUS_ENUM
from ..utils import is_placeholder


class EnumValidator(BaseValidator):
    """Validates enum values."""

    def validate(self, config: Dict[str, Any]) -> ValidationResult:
        self.reset()

        if "role" in config and "level" in config["role"]:
            level = config["role"]["level"]
            if not is_placeholder(level) and level not in LEVEL_ENUM:
                error = ValidationError(
                    field="role.level",
                    message=f"Invalid role.level: {level}. Must be one of: {sorted(LEVEL_ENUM)}",
                    severity="error",
                )
                error.suggestion = f"Use one of: {', '.join(sorted(LEVEL_ENUM))}"
                self.errors.append(error)

        if "lifecycle" in config and "status" in config["lifecycle"]:
            status = config["lifecycle"]["status"]
            if not is_placeholder(status) and status not in STATUS_ENUM:
                error = ValidationError(
                    field="lifecycle.status",
                    message=f"Invalid lifecycle.status: {status}. Must be one of: {sorted(STATUS_ENUM)}",
                    severity="error",
                )
                error.suggestion = f"Use one of: {', '.join(sorted(STATUS_ENUM))}"
                self.errors.append(error)

        if "spec" in config and "status" in config["spec"]:
            status = config["spec"]["status"]
            if not is_placeholder(status) and status not in SPEC_STATUS_ENUM:
                error = ValidationError(
                    field="spec.status",
                    message=f"Invalid spec.status: {status}. Must be one of: {sorted(SPEC_STATUS_ENUM)}",
                    severity="error",
                )
                error.suggestion = f"Use one of: {', '.join(sorted(SPEC_STATUS_ENUM))}"
                self.errors.append(error)

        return self._create_result()
