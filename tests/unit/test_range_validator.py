"""Tests for RangeValidator."""

import pytest
from tooling.validators import RangeValidator


class TestRangeValidator:
    """Tests for RangeValidator class."""

    def test_validate_valid_config(self, valid_config):
        validator = RangeValidator()
        result = validator.validate(valid_config)
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_valid_confidence_threshold(self):
        config = {"guardrails": {"confidence_threshold": 0.95}}
        validator = RangeValidator()
        result = validator.validate(config)
        assert result.is_valid is True

    def test_validate_confidence_threshold_upper_bound(self):
        config = {"guardrails": {"confidence_threshold": 1.0}}
        validator = RangeValidator()
        result = validator.validate(config)
        assert result.is_valid is True

    def test_validate_confidence_threshold_lower_bound(self):
        config = {"guardrails": {"confidence_threshold": 0.0}}
        validator = RangeValidator()
        result = validator.validate(config)
        assert result.is_valid is True

    def test_validate_invalid_confidence_threshold_too_high(self):
        config = {"guardrails": {"confidence_threshold": 1.5}}
        validator = RangeValidator()
        result = validator.validate(config)
        assert result.is_valid is False
        assert any("confidence_threshold" in e.message for e in result.errors)

    def test_validate_invalid_confidence_threshold_negative(self):
        config = {"guardrails": {"confidence_threshold": -0.1}}
        validator = RangeValidator()
        result = validator.validate(config)
        assert result.is_valid is False

    def test_validate_valid_temperature(self):
        config = {"ai_settings": {"generation_params": {"temperature": 0.7}}}
        validator = RangeValidator()
        result = validator.validate(config)
        assert result.is_valid is True

    def test_validate_invalid_temperature_too_high(self):
        config = {"ai_settings": {"generation_params": {"temperature": 1.5}}}
        validator = RangeValidator()
        result = validator.validate(config)
        assert result.is_valid is False

    def test_validate_invalid_temperature_negative(self):
        config = {"ai_settings": {"generation_params": {"temperature": -0.5}}}
        validator = RangeValidator()
        result = validator.validate(config)
        assert result.is_valid is False

    def test_validate_valid_top_p(self):
        config = {"ai_settings": {"generation_params": {"top_p": 0.9}}}
        validator = RangeValidator()
        result = validator.validate(config)
        assert result.is_valid is True

    def test_validate_invalid_top_p(self):
        config = {"ai_settings": {"generation_params": {"top_p": 1.1}}}
        validator = RangeValidator()
        result = validator.validate(config)
        assert result.is_valid is False

    def test_validate_valid_frequency_penalty(self):
        config = {"ai_settings": {"generation_params": {"frequency_penalty": 0.5}}}
        validator = RangeValidator()
        result = validator.validate(config)
        assert result.is_valid is True

    def test_validate_frequency_penalty_upper_bound(self):
        config = {"ai_settings": {"generation_params": {"frequency_penalty": 2.0}}}
        validator = RangeValidator()
        result = validator.validate(config)
        assert result.is_valid is True

    def test_validate_frequency_penalty_lower_bound(self):
        config = {"ai_settings": {"generation_params": {"frequency_penalty": -2.0}}}
        validator = RangeValidator()
        result = validator.validate(config)
        assert result.is_valid is True

    def test_validate_invalid_frequency_penalty_too_high(self):
        config = {"ai_settings": {"generation_params": {"frequency_penalty": 2.5}}}
        validator = RangeValidator()
        result = validator.validate(config)
        assert result.is_valid is False

    def test_validate_invalid_frequency_penalty_too_low(self):
        config = {"ai_settings": {"generation_params": {"frequency_penalty": -2.5}}}
        validator = RangeValidator()
        result = validator.validate(config)
        assert result.is_valid is False

    def test_validate_valid_presence_penalty(self):
        config = {"ai_settings": {"generation_params": {"presence_penalty": 0.3}}}
        validator = RangeValidator()
        result = validator.validate(config)
        assert result.is_valid is True

    def test_validate_invalid_presence_penalty(self):
        config = {"ai_settings": {"generation_params": {"presence_penalty": 3.0}}}
        validator = RangeValidator()
        result = validator.validate(config)
        assert result.is_valid is False

    def test_validate_multiple_ranges_some_invalid(self):
        config = {
            "guardrails": {"confidence_threshold": 0.8},
            "ai_settings": {
                "generation_params": {
                    "temperature": 0.7,
                    "top_p": 1.5,
                    "frequency_penalty": -3.0,
                }
            },
        }
        validator = RangeValidator()
        result = validator.validate(config)
        assert result.is_valid is False
        assert len(result.errors) == 2

    def test_validate_missing_range_fields_no_errors(self):
        config = {"guardrails": {"max_spend_per_task": 100}}
        validator = RangeValidator()
        result = validator.validate(config)
        assert result.is_valid is True

    def test_validate_empty_config(self):
        config = {}
        validator = RangeValidator()
        result = validator.validate(config)
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_non_numeric_value_no_error(self):
        config = {"guardrails": {"confidence_threshold": "high"}}
        validator = RangeValidator()
        result = validator.validate(config)
        assert result.is_valid is True
