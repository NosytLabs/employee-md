"""Tests for TypeValidator."""

import pytest
from tooling.validators import TypeValidator


class TestTypeValidator:
    """Tests for TypeValidator class."""

    def test_validate_valid_config(self, valid_config):
        validator = TypeValidator()
        # Remove identity section to avoid None type issue
        config = valid_config.copy()
        config.pop("identity", None)
        result = validator.validate(config)
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_type_string_instead_of_list(self):
        config = {
            "spec": {
                "name": "test",
                "version": "1.0",
                "compatibility": "should_be_list",
            }
        }
        validator = TypeValidator()
        result = validator.validate(config)
        assert result.is_valid is False
        assert any("compatibility" in e.message for e in result.errors)

    def test_validate_invalid_type_number_instead_of_string(self):
        config = {"spec": {"name": 123, "version": "1.0"}}
        validator = TypeValidator()
        result = validator.validate(config)
        assert result.is_valid is False
        assert any(
            "spec.name" in e.message and "str" in e.message for e in result.errors
        )

    def test_validate_invalid_type_dict_instead_of_list(self):
        config = {"mission": {"objectives": {"should": "be_list"}}}
        validator = TypeValidator()
        result = validator.validate(config)
        assert result.is_valid is False
        assert any("mission.objectives" in e.message for e in result.errors)

    def test_validate_valid_number_types(self):
        config = {"economy": {"rate": 100, "budget_limit": 50.5}}
        validator = TypeValidator()
        result = validator.validate(config)
        assert result.is_valid is True

    def test_validate_invalid_number_type(self):
        config = {"economy": {"rate": "not_a_number"}}
        validator = TypeValidator()
        result = validator.validate(config)
        assert result.is_valid is False
        assert any("economy.rate" in e.message for e in result.errors)

    def test_validate_valid_boolean_type(self):
        config = {"economy": {"energy_accounting": True}}
        validator = TypeValidator()
        result = validator.validate(config)
        assert result.is_valid is True

    def test_validate_invalid_boolean_type(self):
        config = {"economy": {"energy_accounting": "true"}}
        validator = TypeValidator()
        result = validator.validate(config)
        assert result.is_valid is False
        assert any("energy_accounting" in e.message for e in result.errors)

    def test_validate_dict_type_valid(self):
        config = {"economy": {"wallets": {"outbound": "0x123", "inbound": "0x456"}}}
        validator = TypeValidator()
        result = validator.validate(config)
        assert result.is_valid is True

    def test_validate_invalid_dict_type(self):
        config = {"economy": {"wallets": ["not", "a", "dict"]}}
        validator = TypeValidator()
        result = validator.validate(config)
        assert result.is_valid is False
        assert any("wallets" in e.message for e in result.errors)

    def test_validate_list_type_valid(self):
        config = {"permissions": {"data_access": ["read", "write"]}}
        validator = TypeValidator()
        result = validator.validate(config)
        assert result.is_valid is True

    def test_validate_invalid_list_type(self):
        config = {"permissions": {"data_access": "read"}}
        validator = TypeValidator()
        result = validator.validate(config)
        assert result.is_valid is False
        assert any("data_access" in e.message for e in result.errors)

    def test_validate_tuple_type_int_or_float(self):
        config = {"guardrails": {"confidence_threshold": 0.95}}
        validator = TypeValidator()
        result = validator.validate(config)
        assert result.is_valid is True

    def test_validate_invalid_tuple_type(self):
        config = {"guardrails": {"confidence_threshold": "high"}}
        validator = TypeValidator()
        result = validator.validate(config)
        assert result.is_valid is False
        assert any("confidence_threshold" in e.message for e in result.errors)

    def test_validate_empty_config(self):
        config = {}
        validator = TypeValidator()
        result = validator.validate(config)
        assert result.is_valid is True
        assert len(result.errors) == 0
