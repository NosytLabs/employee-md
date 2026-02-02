"""Tests for EnumValidator."""

import pytest
from tooling.validators import EnumValidator


class TestEnumValidator:
    """Tests for EnumValidator class."""

    def test_validate_valid_config(self, valid_config):
        validator = EnumValidator()
        result = validator.validate(valid_config)
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_valid_role_levels(self):
        valid_levels = ["junior", "mid", "senior", "lead"]
        validator = EnumValidator()

        for level in valid_levels:
            config = {
                "role": {"title": "Agent", "level": level},
                "lifecycle": {"status": "active"},
            }
            result = validator.validate(config)
            assert result.is_valid is True

    def test_validate_invalid_role_level(self, invalid_config_invalid_level):
        validator = EnumValidator()
        result = validator.validate(invalid_config_invalid_level)
        assert result.is_valid is False
        assert any("role.level" in e.message for e in result.errors)

    def test_validate_valid_lifecycle_statuses(self):
        valid_statuses = ["onboarding", "active", "suspended", "terminated"]
        validator = EnumValidator()

        for status in valid_statuses:
            config = {
                "role": {"title": "Agent", "level": "senior"},
                "lifecycle": {"status": status},
            }
            result = validator.validate(config)
            assert result.is_valid is True

    def test_validate_invalid_lifecycle_status(self):
        config = {
            "role": {"title": "Agent", "level": "senior"},
            "lifecycle": {"status": "inactive"},
        }
        validator = EnumValidator()
        result = validator.validate(config)
        assert result.is_valid is False
        assert any("lifecycle.status" in e.message for e in result.errors)

    def test_validate_valid_spec_statuses(self):
        valid_statuses = ["draft", "stable", "deprecated"]
        validator = EnumValidator()

        for status in valid_statuses:
            config = {"spec": {"name": "test", "version": "1.0", "status": status}}
            result = validator.validate(config)
            assert result.is_valid is True

    def test_validate_invalid_spec_status(self):
        config = {"spec": {"name": "test", "version": "1.0", "status": "alpha"}}
        validator = EnumValidator()
        result = validator.validate(config)
        assert result.is_valid is False
        assert any("spec.status" in e.message for e in result.errors)

    def test_validate_placeholder_values_skipped(self):
        config = {
            "role": {"title": "Agent", "level": "string"},
            "lifecycle": {"status": "string"},
            "spec": {"name": "test", "version": "1.0", "status": "string"},
        }
        validator = EnumValidator()
        result = validator.validate(config)
        assert result.is_valid is True

    def test_validate_missing_sections_no_errors(self):
        config = {}
        validator = EnumValidator()
        result = validator.validate(config)
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_partial_sections(self):
        config = {"role": {"title": "Agent", "level": "senior"}}
        validator = EnumValidator()
        result = validator.validate(config)
        assert result.is_valid is True

    def test_validate_multiple_invalid_enums(self):
        config = {
            "role": {"title": "Agent", "level": "expert"},
            "lifecycle": {"status": "inactive"},
            "spec": {"name": "test", "version": "1.0", "status": "beta"},
        }
        validator = EnumValidator()
        result = validator.validate(config)
        assert result.is_valid is False
        assert len(result.errors) == 3
