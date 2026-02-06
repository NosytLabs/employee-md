## 2025-02-18 - Safe Caching of Validation Functions
**Learning:** `functools.lru_cache` fails on unhashable inputs (lists, dicts). In this codebase, validation functions like `validate_url` are sometimes called with non-string types (e.g. from parsed YAML/JSON), requiring a type-checking wrapper before the cached implementation.
**Action:** Always implement a public wrapper that filters unhashable types before calling a cached private implementation (`_impl`).
