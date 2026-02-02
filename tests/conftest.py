"""Pytest fixtures and configuration."""

import pytest
from pathlib import Path

from tooling.employee_validator import EmployeeValidationOrchestrator


VALID_CONFIG = {
    "spec": {
        "name": "employee.md",
        "version": "1.0",
        "kind": "agent-employment",
        "status": "stable",
        "schema": "https://example.com/schema.json",
        "license": "MIT",
        "homepage": "https://example.com",
    },
    "role": {
        "title": "Test Agent",
        "level": "senior",
        "department": "Engineering",
        "work_location": "remote",
        "employment_type": "full_time",
    },
    "lifecycle": {
        "status": "active",
        "start_date": "2024-01-01",
    },
    "identity": {
        "agent_id": "agent-123",
        "version": "1.0",
        "wallet": None,
    },
}


@pytest.fixture
def valid_config():
    """Return a valid configuration."""
    return VALID_CONFIG.copy()


@pytest.fixture
def invalid_config_missing_level():
    """Return a config missing required role.level field."""
    config = VALID_CONFIG.copy()
    config["role"].pop("level", None)
    return config


@pytest.fixture
def invalid_config_invalid_level():
    """Return a config with invalid role.level."""
    config = VALID_CONFIG.copy()
    config["role"]["level"] = "super-senior"
    return config


@pytest.fixture
def orchestrator():
    """Return a validation orchestrator."""
    return EmployeeValidationOrchestrator(use_cache=False)


@pytest.fixture
def example_files_dir():
    """Return path to examples directory."""
    return Path(__file__).parent.parent.parent / "examples"


@pytest.fixture
def examples_dir():
    """Return path to examples directory (alias for example_files_dir)."""
    return Path(__file__).parent.parent.parent / "examples"
