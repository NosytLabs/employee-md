import pytest
import yaml
import os
from tooling.validate import EmployeeValidator

# Sample valid config
VALID_CONFIG = {
    "spec": {
        "name": "employee.md",
        "version": "1.0",
        "kind": "agent-employment"
    },
    "role": {
        "title": "Test Agent",
        "level": "senior"
    },
    "lifecycle": {
        "status": "active"
    }
}

# Sample invalid config (missing required field)
INVALID_CONFIG = {
    "role": {
        "title": "Test Agent"
        # Missing level
    },
    "lifecycle": {
        "status": "active"
    }
}

def test_validate_valid_config():
    validator = EmployeeValidator(VALID_CONFIG)
    assert validator.validate() is True
    assert len(validator.errors) == 0

def test_validate_invalid_config():
    validator = EmployeeValidator(INVALID_CONFIG)
    assert validator.validate() is False
    assert len(validator.errors) > 0
    assert "Missing required field: 'role.level'" in validator.errors

def test_validate_enums():
    config = VALID_CONFIG.copy()
    config["role"]["level"] = "super-senior" # Invalid enum
    validator = EmployeeValidator(config)
    assert validator.validate() is False
    assert any("Invalid role.level" in e for e in validator.errors)

def test_validate_types():
    config = VALID_CONFIG.copy()
    config["economy"] = {
        "rate": "not-a-number" # Should be number
    }
    validator = EmployeeValidator(config)
    assert validator.validate() is False
    assert any("Invalid type" in e for e in validator.errors)

def test_placeholder_skipping():
    config = VALID_CONFIG.copy()
    config["role"]["level"] = "string" # Placeholder
    validator = EmployeeValidator(config)
    # Should pass because placeholders are skipped
    assert validator.validate() is True
