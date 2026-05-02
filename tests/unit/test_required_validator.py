"""Tests for RequiredFieldValidator."""

import pytest
from tooling.validators import RequiredFieldValidator


class TestRequiredFieldValidator:
    """Tests for RequiredFieldValidator class."""

    def test_validate_valid_config(self, valid_config):
        validator = RequiredFieldValidator()
        result = validator.validate(valid_config)
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_missing_role_section(self):
        config = {"lifecycle": {"status": "active"}}
        validator = RequiredFieldValidator()
        result = validator.validate(config)
        assert result.is_valid is False
        assert any(
            "Missing required section: 'role'" in e.message for e in result.errors
        )

    def test_validate_missing_lifecycle_section(self):
        config = {"role": {"title": "Agent", "level": "senior"}}
        validator = RequiredFieldValidator()
        result = validator.validate(config)
        assert result.is_valid is False
        assert any(
            "Missing required section: 'lifecycle'" in e.message for e in result.errors
        )

    def test_validate_missing_role_title(self):
        config = {"role": {"level": "senior"}, "lifecycle": {"status": "active"}}
        validator = RequiredFieldValidator()
        result = validator.validate(config)
        assert result.is_valid is False
        assert any("role.title" in e.message for e in result.errors)

    def test_validate_missing_role_level(self, invalid_config_missing_level):
        validator = RequiredFieldValidator()
        result = validator.validate(invalid_config_missing_level)
        assert result.is_valid is False
        assert any("role.level" in e.message for e in result.errors)

    def test_validate_missing_lifecycle_status(self):
        config = {
            "role": {"title": "Agent", "level": "senior"},
            "lifecycle": {"start_date": "2024-01-01"},
        }
        validator = RequiredFieldValidator()
        result = validator.validate(config)
        assert result.is_valid is False
        assert any("lifecycle.status" in e.message for e in result.errors)

    def test_validate_all_missing_required(self):
        config = {}
        validator = RequiredFieldValidator()
        result = validator.validate(config)
        assert result.is_valid is False
        assert len(result.errors) == 2

    def test_reset_clears_errors(self, invalid_config_missing_level):
        validator = RequiredFieldValidator()
        result1 = validator.validate(invalid_config_missing_level)
        assert len(result1.errors) > 0

        validator.reset()
        assert len(validator.errors) == 0
        assert len(validator.warnings) == 0
