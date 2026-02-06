"""Utility functions for validation."""

import os
import sys
from datetime import datetime
from functools import lru_cache
from urllib.parse import urlparse
from typing import Any, Dict, Optional
from .constants import (
    PLACEHOLDER_VALUES,
    ISO_DATE_CACHE_SIZE,

)


class Color:
    """ANSI color codes for terminal output."""

    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    RESET = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

    @staticmethod
    def style(text: str, *styles: str) -> str:
        """Apply styles to text if connected to a TTY."""
        if not sys.stdout.isatty() and not os.environ.get("FORCE_COLOR"):
            return text
        return "".join(styles) + text + Color.RESET

BECH32_CHARS = set("023456789acdefghjklmnpqrstuvwxyz")
BASE58_CHARS = set("123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz")


def is_placeholder(value: Any) -> bool:
    """Check if value is a placeholder.

    Returns True for:
    - None values
    - String values in PLACEHOLDER_VALUES (case-insensitive)

    Returns False for non-string non-None values (these are real values, not placeholders).
    """
    if value is None:
        return True
    if not isinstance(value, str):
        return False
    if value.strip().lower() in PLACEHOLDER_VALUES:
        return True
    return False


@lru_cache(maxsize=ISO_DATE_CACHE_SIZE)
def validate_iso_date(date_str: str) -> bool:
    """Validate ISO 8601 date format.

    Supports:
    - 2024-01-15
    - 2024-01-15T10:30:00
    - 2024-01-15T10:30:00Z
    - 2024-01-15T10:30:00+00:00

    Cached for performance optimization.
    """
    if not isinstance(date_str, str):
        return False
    if is_placeholder(date_str):
        return True
    try:
        datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return True
    except (ValueError, TypeError):
        return False


def validate_wallet(wallet: str) -> bool:
    """Validate crypto wallet address format securely.

    Uses safe validation without complex regex to prevent ReDoS.

    Args:
        wallet: Wallet address string

    Returns:
        True if wallet is a valid crypto address format or placeholder, False otherwise
    """
    # None is treated as placeholder/acceptable
    if wallet is None:
        return True

    if not isinstance(wallet, str):
        return False

    # Empty string or string placeholders are acceptable
    if not wallet or is_placeholder(wallet):
        return True

    # Ethereum/EVM: 0x + 40 hex chars
    if wallet.startswith("0x"):
        if len(wallet) != 42:
            return False
        try:
            int(wallet[2:], 16)
            return True
        except ValueError:
            return False

    # Bitcoin Legacy (1... or 3...): 26-35 chars, base58
    if wallet.startswith(("1", "3")):
        if not (26 <= len(wallet) <= 35):
            return False
        # Check for valid base58 characters
        return all(c in BASE58_CHARS for c in wallet)

    # Bitcoin Bech32 (bc1...): 42-62 chars
    if wallet.startswith("bc1"):
        if not (42 <= len(wallet) <= 62):
            return False
        # Bech32 characters: lowercase alphanumeric except 1, b, i, o
        return all(c in BECH32_CHARS for c in wallet[3:])

    # Solana: Base58, 32-44 chars, must be all base58 chars
    # Only return True if it doesn't match other patterns
    if 32 <= len(wallet) <= 44:
        if all(c in BASE58_CHARS for c in wallet):
            return True

    return False


def validate_url(url: Any) -> bool:
    """Validate URL format securely without regex.

    Uses urllib.parse to avoid ReDoS vulnerabilities.

    Args:
        url: URL string to validate

    Returns:
        True if valid URL or placeholder, False otherwise
    """
    # None is treated as placeholder/acceptable
    if url is None:
        return True

    if not isinstance(url, str):
        return False

    if not url or is_placeholder(url):
        return True

    try:
        parsed = urlparse(url)
        return bool(parsed.scheme in ("http", "https") and parsed.netloc)
    except (ValueError, TypeError):
        return False


def validate_email(email: Any) -> bool:
    """Validate email format.

    Uses a safe pattern without catastrophic backtracking.

    Args:
        email: Email string to validate

    Returns:
        True if valid email or placeholder, False otherwise
    """
    # None is treated as placeholder/acceptable
    if email is None:
        return True

    if not isinstance(email, str):
        return False

    if not email or is_placeholder(email):
        return True

    # Basic structure check first
    if "@" not in email or email.count("@") != 1:
        return False

    local, domain = email.rsplit("@", 1)

    # Local part checks
    if not local or len(local) > 64:
        return False
    if local.startswith(".") or local.endswith("."):
        return False
    if ".." in local:
        return False

    # Domain checks
    if not domain or len(domain) > 253:
        return False
    if "." not in domain:
        return False
    if domain.startswith(".") or domain.endswith("."):
        return False
    if ".." in domain:
        return False

    return True


def get_nested_value(data: Dict[str, Any], path: str) -> Optional[Any]:
    """Get a nested value from a dictionary using dot notation."""
    if not path:
        return data
    keys = path.split(".")
    current: Any = data
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
        if current is None:
            return None
    return current


def check_type(value: Any, expected_type: Any) -> bool:
    """Check if value matches expected type.

    Placeholder values (strings like 'TBD', 'TODO', etc.) pass type checks
    since they indicate fields not yet filled in.
    """
    if value is None:
        return False

    # String placeholders pass all type checks
    if isinstance(value, str) and is_placeholder(value):
        return True

    # Non-string placeholders don't pass type checks
    if is_placeholder(value):
        return False

    if isinstance(expected_type, tuple):
        return isinstance(value, expected_type)

    return isinstance(value, expected_type)
