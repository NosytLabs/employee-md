"""Tests for FormatValidator."""

import pytest
from tooling.validators import FormatValidator


class TestFormatValidator:
    """Tests for FormatValidator class."""

    def test_validate_valid_config(self, valid_config):
        validator = FormatValidator()
        # Remove wallet field since it might be invalid
        config = valid_config.copy()
        if "identity" in config and "wallet" in config["identity"]:
            config["identity"]["wallet"] = None
        result = validator.validate(config)
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_wallet_none_allowed(self):
        config = {"identity": {"wallet": None}}
        validator = FormatValidator()
        result = validator.validate(config)
        assert result.is_valid is True

    def test_validate_invalid_ethereum_wallet_too_short(self):
        config = {"identity": {"wallet": "0x123"}}
        validator = FormatValidator()
        result = validator.validate(config)
        assert result.is_valid is False
        assert any("wallet" in e.message for e in result.errors)

    def test_validate_invalid_ethereum_wallet_invalid_chars(self):
        config = {"identity": {"wallet": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bGh"}}
        validator = FormatValidator()
        result = validator.validate(config)
        assert result.is_valid is False

    def test_validate_valid_bitcoin_legacy_wallet(self):
        config = {"identity": {"wallet": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"}}
        validator = FormatValidator()
        result = validator.validate(config)
        assert result.is_valid is True

    def test_validate_valid_bitcoin_segwit_wallet(self):
        config = {"identity": {"wallet": "3J98t1WpEZ73CNmYviecrnyiWrnqRhWNLy"}}
        validator = FormatValidator()
        result = validator.validate(config)
        assert result.is_valid is True

    def test_validate_valid_bitcoin_bech32_wallet(self):
        config = {"identity": {"wallet": "bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq"}}
        validator = FormatValidator()
        result = validator.validate(config)
        assert result.is_valid is True

    def test_validate_invalid_bitcoin_wallet_too_short(self):
        config = {"identity": {"wallet": "1abc"}}
        validator = FormatValidator()
        result = validator.validate(config)
        assert result.is_valid is False

    def test_validate_valid_solana_wallet(self):
        config = {
            "identity": {"wallet": "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM"}
        }
        validator = FormatValidator()
        result = validator.validate(config)
        assert result.is_valid is True

    def test_validate_invalid_wallet_none(self):
        config = {"identity": {"wallet": None}}
        validator = FormatValidator()
        result = validator.validate(config)
        assert result.is_valid is True

    def test_validate_valid_iso_date(self):
        config = {"lifecycle": {"start_date": "2024-01-15"}}
        validator = FormatValidator()
        result = validator.validate(config)
        assert result.is_valid is True

    def test_validate_valid_iso_datetime(self):
        config = {"lifecycle": {"start_date": "2024-01-15T10:30:00"}}
        validator = FormatValidator()
        result = validator.validate(config)
        assert result.is_valid is True

    def test_validate_valid_iso_datetime_with_z(self):
        config = {"lifecycle": {"start_date": "2024-01-15T10:30:00Z"}}
        validator = FormatValidator()
        result = validator.validate(config)
        assert result.is_valid is True

    def test_validate_valid_iso_datetime_with_timezone(self):
        config = {"lifecycle": {"start_date": "2024-01-15T10:30:00+00:00"}}
        validator = FormatValidator()
        result = validator.validate(config)
        assert result.is_valid is True

    def test_validate_invalid_date_format(self):
        config = {"lifecycle": {"start_date": "01/15/2024"}}
        validator = FormatValidator()
        result = validator.validate(config)
        assert result.is_valid is False
        assert any("start_date" in e.message for e in result.errors)

    def test_validate_valid_http_url(self):
        config = {"knowledge_base": {"documentation_urls": ["http://example.com"]}}
        validator = FormatValidator()
        result = validator.validate(config)
        assert result.is_valid is True

    def test_validate_valid_https_url(self):
        config = {
            "knowledge_base": {"documentation_urls": ["https://example.com/docs"]}
        }
        validator = FormatValidator()
        result = validator.validate(config)
        assert result.is_valid is True

    def test_validate_invalid_url_no_scheme(self):
        config = {"knowledge_base": {"documentation_urls": ["example.com"]}}
        validator = FormatValidator()
        result = validator.validate(config)
        assert result.is_valid is False

    def test_validate_invalid_url_ftp_scheme(self):
        config = {"knowledge_base": {"documentation_urls": ["ftp://example.com"]}}
        validator = FormatValidator()
        result = validator.validate(config)
        assert result.is_valid is False

    def test_validate_invalid_url_empty_netloc(self):
        config = {"knowledge_base": {"documentation_urls": ["https://"]}}
        validator = FormatValidator()
        result = validator.validate(config)
        assert result.is_valid is False

    def test_validate_multiple_urls_one_invalid(self):
        config = {
            "knowledge_base": {
                "documentation_urls": [
                    "https://example.com/docs",
                    "invalid-url",
                    "https://another.com",
                ]
            }
        }
        validator = FormatValidator()
        result = validator.validate(config)
        assert result.is_valid is False

    def test_validate_empty_config(self):
        config = {}
        validator = FormatValidator()
        result = validator.validate(config)
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_placeholder_values_skipped(self):
        config = {
            "identity": {"wallet": "string"},
            "lifecycle": {"start_date": "string"},
            "knowledge_base": {"documentation_urls": ["string"]},
        }
        validator = FormatValidator()
        result = validator.validate(config)
        assert result.is_valid is True
