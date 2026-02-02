"""Tests for ValidationCache."""

import pytest
import time
from tooling.cache import ValidationCache, CacheEntry, reset_cache


class TestValidationCache:
    """Tests for ValidationCache class."""

    def test_cache_init(self):
        cache = ValidationCache(max_size=10, default_ttl=60)
        assert cache.max_size == 10
        assert cache.default_ttl == 60

    def test_cache_set_and_get(self):
        cache = ValidationCache()
        data = {"test": "data"}
        result = {"is_valid": True}

        cache.set(data, result)
        retrieved = cache.get(data)

        assert retrieved is not None
        assert retrieved == result

    def test_cache_miss(self):
        cache = ValidationCache()
        data = {"test": "data"}

        result = cache.get(data)
        assert result is None

    def test_cache_expiration(self):
        cache = ValidationCache(default_ttl=0.1)  # 100ms TTL
        data = {"test": "data"}
        result = {"is_valid": True}

        cache.set(data, result)

        time.sleep(0.15)

        result = cache.get(data)
        assert result is None

    def test_cache_eviction_when_full(self):
        cache = ValidationCache(max_size=2)

        for i in range(3):
            cache.set({"data": i}, {"result": i})

        cache_stats = cache.get_stats()
        assert cache_stats["size"] == 2

    def test_cache_custom_ttl(self):
        cache = ValidationCache(default_ttl=60)
        data = {"test": "data"}
        result = {"is_valid": True}

        cache.set(data, result, ttl=0.1)

        time.sleep(0.15)

        result = cache.get(data)
        assert result is None

    def test_cache_clear(self):
        cache = ValidationCache()

        for i in range(5):
            cache.set({"data": i}, {"result": i})

        assert cache.get_stats()["size"] == 5

        cache.clear()

        assert cache.get_stats()["size"] == 0

    def test_cache_different_data_different_keys(self):
        cache = ValidationCache()

        data1 = {"test": "data1"}
        data2 = {"test": "data2"}

        cache.set(data1, {"result": 1})
        cache.set(data2, {"result": 2})

        assert cache.get(data1) == {"result": 1}
        assert cache.get(data2) == {"result": 2}

    def test_cache_same_data_same_key(self):
        cache = ValidationCache()

        data = {"test": "data"}

        cache.set(data, {"result": 1})
        cache.set(data, {"result": 2})

        assert cache.get(data) == {"result": 2}

    def test_cache_stats(self):
        cache = ValidationCache(max_size=5, default_ttl=60)

        stats = cache.get_stats()

        assert stats["size"] == 0
        assert stats["max_size"] == 5

        for i in range(3):
            cache.set({"data": i}, {"result": i})

        stats = cache.get_stats()
        assert stats["size"] == 3

    def test_global_cache_singleton(self):
        from tooling.cache import get_cache

        cache1 = get_cache()
        cache2 = get_cache()

        assert cache1 is cache2

    def test_reset_global_cache(self):
        from tooling.cache import get_cache

        cache = get_cache()
        cache.set({"test": "data"}, {"result": 1})

        assert cache.get_stats()["size"] == 1

        reset_cache()

        assert cache.get_stats()["size"] == 0

    def test_cache_entry_creation(self):
        entry = CacheEntry(result={"test": "result"}, timestamp=time.time(), ttl=60)

        assert entry.result == {"test": "result"}
        assert entry.ttl == 60

    def test_cache_uses_hash_for_key(self):
        cache = ValidationCache()

        data = {"test": "data", "nested": {"value": 123}}

        cache.set(data, {"result": 1})
        cache.set(data, {"result": 2})

        assert cache.get_stats()["size"] == 1

    def test_cache_with_complex_data(self):
        cache = ValidationCache()

        complex_data = {
            "spec": {"name": "test", "version": "1.0"},
            "role": {"title": "Agent", "level": "senior"},
            "lifecycle": {"status": "active"},
        }

        result = {"is_valid": True, "errors": [], "warnings": []}

        cache.set(complex_data, result)
        retrieved = cache.get(complex_data)

        assert retrieved == result
