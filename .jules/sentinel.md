# Sentinel's Journal

## 2025-02-18 - Symlink Traversal via Absolute Paths
**Vulnerability:** `SecureYAMLParser._is_safe_path` allowed symlink traversal because it assumed absolute paths were already resolved and safe from `..` traversal, skipping `path.resolve()`.
**Learning:** Checking `path.is_absolute()` does not guarantee that the path is canonical or free of symlinks that point outside allowed directories.
**Prevention:** Always use `path.resolve()` to canonicalize paths before performing security checks, regardless of whether the path is absolute or relative.
