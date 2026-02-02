"""Caching module for validation results."""

import hashlib
import threading
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

from .constants import DEFAULT_CACHE_MAX_SIZE, DEFAULT_CACHE_TTL
from .monitoring import get_metrics


@dataclass
class CacheEntry:
    """A cached validation result."""

    result: Any
    timestamp: float
    ttl: float  # Time to live in seconds


class ValidationCache:
    """LRU cache for validation results."""

    def __init__(
        self,
        max_size: int = DEFAULT_CACHE_MAX_SIZE,
        default_ttl: float = DEFAULT_CACHE_TTL,
    ) -> None:
        """
        Initialize cache.

        Args:
            max_size: Maximum number of entries in cache
            default_ttl: Default time-to-live in seconds (5 minutes)
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = threading.Lock()
        self._metrics = get_metrics()

    def _normalize_data(self, value: Any) -> Any:
        if isinstance(value, dict):
            return tuple(
                (str(key), self._normalize_data(val))
                for key, val in sorted(value.items(), key=lambda item: str(item[0]))
            )
        if isinstance(value, list):
            return tuple(self._normalize_data(item) for item in value)
        if isinstance(value, set):
            return tuple(
                sorted((self._normalize_data(item) for item in value), key=str)
            )
        if isinstance(value, tuple):
            return tuple(self._normalize_data(item) for item in value)
        return value

    def _compute_hash(self, data: Dict[str, Any]) -> str:
        """Compute hash of data for cache key."""
        try:
            normalized = self._normalize_data(data)
            content = repr(normalized)
        except (TypeError, AttributeError):
            content = str(data)
        return hashlib.sha256(content.encode()).hexdigest()

    def get(
        self, data: Optional[Dict[str, Any]] = None, key: Optional[str] = None
    ) -> Optional[Any]:
        """Get cached result if available and not expired.

        Args:
            data: The data to look up in cache

        Returns:
            Cached result if found and not expired, None otherwise
        """
        if key is None:
            if data is None:
                return None
            key = self._compute_hash(data)

        with self._lock:
            entry = self._cache.get(key)

        if entry is None:
            self._metrics.record_cache_miss()
            return None

        # Check if expired
        if time.time() - entry.timestamp > entry.ttl:
            with self._lock:
                self._cache.pop(key, None)
                self._metrics.record_cache_size(len(self._cache), self.max_size)
            self._metrics.record_cache_miss()
            return None

        self._metrics.record_cache_hit()
        return entry.result

    def set(
        self,
        data: Optional[Dict[str, Any]],
        result: Any,
        ttl: Optional[float] = None,
        key: Optional[str] = None,
    ) -> None:
        """Cache a validation result.

        Args:
            data: The data to cache result for
            result: The validation result to cache
            ttl: Optional time-to-live override
        """
        if key is None:
            if data is None:
                return
            key = self._compute_hash(data)

        with self._lock:
            evicted = False
            if len(self._cache) >= self.max_size:
                evicted = True
                oldest_key = min(
                    self._cache.keys(), key=lambda k: self._cache[k].timestamp
                )
                del self._cache[oldest_key]

            self._cache[key] = CacheEntry(
                result=result, timestamp=time.time(), ttl=ttl or self.default_ttl
            )

            self._metrics.record_cache_size(len(self._cache), self.max_size)
            if evicted:
                self._metrics.record_cache_eviction()

    def clear(self) -> None:
        """Clear all cached entries."""
        with self._lock:
            self._cache.clear()
            self._metrics.record_cache_size(0, self.max_size)

    def get_stats(self) -> Dict[str, int]:
        """Get cache statistics.

        Returns:
            Dictionary with 'size' and 'max_size' keys
        """
        with self._lock:
            return {
                "size": len(self._cache),
                "max_size": self.max_size,
            }


# Global cache instance
_global_cache = ValidationCache()
_global_cache_lock = threading.Lock()


def get_cache() -> ValidationCache:
    """Get the global validation cache."""
    with _global_cache_lock:
        return _global_cache


def reset_cache() -> None:
    """Reset the global validation cache."""
    with _global_cache_lock:
        _global_cache.clear()
