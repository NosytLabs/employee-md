"""Tests for utility functions."""

import pytest
from tooling.utils import (
    is_placeholder,
    validate_iso_date,
    validate_wallet,
    validate_url,
    validate_email,
    get_nested_value,
    check_type,
)


class TestIsPlaceholder:
    """Tests for is_placeholder function."""

    def test_placeholders_true(self):
        """Test that placeholder values return True."""
        assert is_placeholder("TBD")
        assert is_placeholder("TBA")
        assert is_placeholder("tbd")
        assert is_placeholder("tba")
        assert is_placeholder("TODO")
        assert is_placeholder("todo")
        assert is_placeholder("To be determined")
        assert is_placeholder("  TBD  ")
        assert is_placeholder(None)

    def test_non_placeholders_false(self):
        """Test that non-placeholder values return False."""
        assert not is_placeholder("john.doe@example.com")
        assert not is_placeholder("https://example.com")
        assert not is_placeholder("2024-01-15")
        assert not is_placeholder("0x1234567890abcdef1234567890abcdef12345678")
        assert not is_placeholder(123)
        assert not is_placeholder([1, 2, 3])
        assert not is_placeholder({"key": "value"})


class TestValidateIsoDate:
    """Tests for validate_iso_date function."""

    def test_valid_iso_dates(self):
        """Test valid ISO 8601 date formats."""
        assert validate_iso_date("2024-01-15")
        assert validate_iso_date("2024-12-31T10:30:00")
        assert validate_iso_date("2024-12-31T10:30:00Z")
        assert validate_iso_date("2024-12-31T10:30:00+00:00")
        assert validate_iso_date("2024-12-31T10:30:00-05:00")

    def test_placeholder_dates(self):
        """Test that placeholder dates pass."""
        assert validate_iso_date("TBD")
        assert validate_iso_date("TODO")
        assert validate_iso_date("tbd")

    def test_invalid_iso_dates(self):
        """Test invalid date formats."""
        assert not validate_iso_date("2024-13-01")
        assert not validate_iso_date("2024-12-32")
        assert not validate_iso_date("15-01-2024")
        assert not validate_iso_date("2024/01/15")
        assert not validate_iso_date("not a date")

    def test_leap_year_dates(self):
        """Test leap year date validation."""
        assert validate_iso_date("2024-02-29")
        assert not validate_iso_date("2023-02-29")


class TestValidateWallet:
    """Tests for validate_wallet function."""

    def test_placeholder_wallets(self):
        """Test that placeholder wallet addresses pass."""
        assert validate_wallet("TBD")
        assert validate_wallet("")
        assert validate_wallet(None)

    def test_ethereum_wallets(self):
        """Test valid and invalid Ethereum/EVM addresses."""
        assert validate_wallet("0x1234567890abcdef1234567890abcdef12345678")
        assert validate_wallet("0xABCDEF1234567890ABCDEF1234567890ABCDEF12")
        assert validate_wallet("0x" + "a" * 40)

        assert not validate_wallet("0x1234567890abcdef1234567890abcdef123456")
        assert not validate_wallet("0x1234567890abcdef1234567890abcdef123456789")
        assert not validate_wallet("1234567890abcdef1234567890abcdef12345678")
        assert not validate_wallet("0x1234567890abcdef1234567890abcdef1234567g")

    def test_bitcoin_legacy_wallets(self):
        """Test valid and invalid Bitcoin Legacy addresses."""
        assert validate_wallet("1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa")
        assert validate_wallet("3J98t1WpEZ73CNmYviecrnyiWrnqRhWNLy")

        assert not validate_wallet("1A1zP1eP5QGefi2DMPTfTL5SL")  # Too short (25 chars)
        assert not validate_wallet(
            "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa123456"
        )  # Too long (36 chars)
        assert not validate_wallet(
            "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfO"
        )  # Invalid char 'O' not in base58

    def test_bitcoin_bech32_wallets(self):
        """Test valid and invalid Bitcoin Bech32 addresses."""
        assert validate_wallet("bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq")
        assert validate_wallet(
            "bc1qc7slrfxkknqcq2jevvvkdgvrt8080852dfjewde450xdlk4ugp7szr5w0"
        )

        assert not validate_wallet(
            "bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5m"
        )  # Too short (41 chars)
        assert not validate_wallet(
            "bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq" + "a" * 21
        )  # Too long (63 chars)
        assert not validate_wallet(
            "bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdqO"
        )  # Invalid char 'O'

    def test_solana_wallets(self):
        """Test valid and invalid Solana addresses."""
        assert validate_wallet("7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr")
        assert validate_wallet("9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM")

        assert not validate_wallet(
            "7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9"
        )  # Too short (31 chars)
        assert not validate_wallet(
            "7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr123456789"
        )  # Too long (45 chars)
        assert not validate_wallet(
            "7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hO"
        )  # Invalid char 'O'

    def test_non_string_wallets(self):
        """Test that non-string wallets return False."""
        assert not validate_wallet(123)
        assert not validate_wallet([])
        assert not validate_wallet({})


class TestValidateUrl:
    """Tests for validate_url function."""

    def test_placeholder_urls(self):
        """Test that placeholder URLs pass."""
        assert validate_url("TBD")
        assert validate_url("")
        assert validate_url(None)

    def test_valid_http_urls(self):
        """Test valid HTTP URLs."""
        assert validate_url("http://example.com")
        assert validate_url("https://example.com")
        assert validate_url("https://subdomain.example.com/path")
        assert validate_url("https://example.com:443/path?query=value#fragment")
        assert validate_url("http://localhost:8080")
        assert validate_url("https://192.168.1.1")

    def test_invalid_urls(self):
        """Test invalid URL formats."""
        assert not validate_url("example.com")
        assert not validate_url("ftp://example.com")
        assert not validate_url("://example.com")
        assert not validate_url("not a url")
        assert not validate_url("https://")
        assert not validate_url(123)

    def test_non_string_urls(self):
        """Test that non-string URLs return False."""
        assert not validate_url(123)
        assert not validate_url([])
        assert not validate_url({})


class TestValidateEmail:
    """Tests for validate_email function."""

    def test_placeholder_emails(self):
        """Test that placeholder emails pass."""
        assert validate_email("TBD")
        assert validate_email("")
        assert validate_email(None)

    def test_valid_emails(self):
        """Test valid email addresses."""
        assert validate_email("user@example.com")
        assert validate_email("user.name@example.com")
        assert validate_email("user+tag@example.com")
        assert validate_email("user123@example.co.uk")
        assert validate_email("user_name@subdomain.example.com")

    def test_invalid_emails(self):
        """Test invalid email formats."""
        assert not validate_email("@example.com")
        assert not validate_email("user@")
        assert not validate_email("user@.com")
        assert not validate_email("user@com")
        assert not validate_email("user@example..com")
        assert not validate_email(".user@example.com")
        assert not validate_email("user.@example.com")
        assert not validate_email("user..name@example.com")
        assert not validate_email("user@example")  # No TLD

    def test_email_with_multiple_at(self):
        """Test that emails with multiple @ signs fail."""
        assert not validate_email("user@name@example.com")

    def test_email_with_long_parts(self):
        """Test that overly long email parts fail."""
        long_local = "a" * 65 + "@example.com"
        long_domain = "user@" + "a" * 254 + ".com"
        assert not validate_email(long_local)
        assert not validate_email(long_domain)

    def test_non_string_emails(self):
        """Test that non-string emails return False."""
        assert not validate_email(123)
        assert not validate_email([])
        assert not validate_email({})


class TestGetNestedValue:
    """Tests for get_nested_value function."""

    def test_get_simple_value(self):
        """Test getting a simple top-level value."""
        data = {"name": "test"}
        assert get_nested_value(data, "name") == "test"

    def test_get_nested_dict_value(self):
        """Test getting a nested dictionary value."""
        data = {"spec": {"name": "agent", "version": "1.0"}}
        assert get_nested_value(data, "spec.name") == "agent"
        assert get_nested_value(data, "spec.version") == "1.0"

    def test_get_deeply_nested_value(self):
        """Test getting deeply nested values."""
        data = {"level1": {"level2": {"level3": {"value": "deep"}}}}
        assert get_nested_value(data, "level1.level2.level3.value") == "deep"

    def test_get_nonexistent_key(self):
        """Test getting a nonexistent key returns None."""
        data = {"name": "test"}
        assert get_nested_value(data, "nonexistent") is None
        assert get_nested_value(data, "spec.nonexistent") is None

    def test_get_from_non_dict_intermediate(self):
        """Test getting value when intermediate key is not a dict."""
        data = {"name": "test", "list": [1, 2, 3]}
        assert get_nested_value(data, "list.key") is None

    def test_empty_path(self):
        """Test getting value with empty path."""
        data = {"name": "test"}
        assert get_nested_value(data, "") == data

    def test_none_value(self):
        """Test that None values are returned correctly."""
        data = {"value": None}
        assert get_nested_value(data, "value") is None


class TestCheckType:
    """Tests for check_type function."""

    def test_check_string_type(self):
        """Test checking string type."""
        assert check_type("test", str)
        assert not check_type(123, str)

    def test_check_int_type(self):
        """Test checking integer type."""
        assert check_type(123, int)
        assert not check_type("123", int)

    def test_check_list_type(self):
        """Test checking list type."""
        assert check_type([1, 2, 3], list)
        assert not check_type((1, 2, 3), list)

    def test_check_dict_type(self):
        """Test checking dict type."""
        assert check_type({"key": "value"}, dict)
        assert not check_type([1, 2, 3], dict)

    def test_check_tuple_type(self):
        """Test checking tuple type."""
        assert check_type((1, 2, 3), tuple)
        assert not check_type([1, 2, 3], tuple)

    def test_check_union_type(self):
        """Test checking union types."""
        assert check_type("test", (str, int))
        assert check_type(123, (str, int))
        assert not check_type([], (str, int))

    def test_placeholder_values_pass(self):
        """Test that placeholder values pass type check."""
        assert check_type("TBD", str)
        assert check_type("TODO", int)
        assert check_type("tbd", list)

    def test_none_values(self):
        """Test None value handling."""
        assert not check_type(None, str)
        assert not check_type(None, int)

    def test_bool_type(self):
        """Test boolean type check."""
        assert check_type(True, bool)
        assert check_type(False, bool)
        assert not check_type(1, bool)
        assert not check_type("true", bool)
