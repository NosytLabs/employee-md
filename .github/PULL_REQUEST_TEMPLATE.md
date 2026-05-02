# Pull Request

## Summary

<!-- Provide a brief summary of the changes made. -->

Fixes # (issue number)

## Type of Change

<!-- Please check the relevant option(s): -->

- [ ] 🐛 Bug fix (non-breaking change which fixes an issue)
- [ ] ✨ New feature (non-breaking change which adds functionality)
- [ ] 💥 Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] 📚 Documentation update
- [ ] 🔧 Spec version update
- [ ] 🧪 Test addition or update
- [ ] 🎨 Code style/formatting
- [ ] ♻️ Refactoring
- [ ] ⚡ Performance improvement
- [ ] 🔒 Security improvement

## Changes Made

<!-- Describe the changes in detail: -->

### Files Modified

- `file1.py`: Description of changes
- `file2.md`: Description of changes

### Key Changes

1.
2.
3.

## Testing

<!-- Describe the tests you ran. The fastest way to mirror CI locally is `make ci`. -->

```bash
# Full CI gate (lint + format-check + typecheck + tests + permissive + strict schema)
make ci

# Or run the pieces individually:
pytest tests/ -v
ruff check tooling/
ruff format --check tooling/
mypy tooling/ --ignore-missing-imports
make validate          # permissive CLI on all 10 official files
make validate-strict   # strict JSON Schema (Draft 7) on all 10 official files
```

### Test Results

<!-- Paste relevant test output: -->
```
All tests passed!
```

## Checklist

<!-- Please confirm the following: -->

### General
- [ ] My code follows the project's style guidelines
- [ ] I have performed a self-review of my code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] My changes generate no new warnings

### For Spec Changes
- [ ] I have updated `employee.md` with new fields/sections
- [ ] I have updated `tooling/schema.json` to reflect spec changes
- [ ] I have updated all examples in `examples/` directory
- [ ] I have updated version numbers appropriately
- [ ] If I added a new example, it is listed in **both** `make validate` and
      the strict `schema-check` whitelist in `.github/workflows/validate.yml`
- [ ] `make validate-strict` passes against every official example

### Documentation
- [ ] I have made corresponding changes to the documentation
- [ ] I have updated `README.md` if needed
- [ ] I have updated `INTEGRATION.md` if needed
- [ ] I have updated `CHANGELOG.md` with my changes

### Testing
- [ ] I have added tests that prove my fix/feature works
- [ ] New and existing unit tests pass locally
- [ ] I have validated all example files
- [ ] Schema validation passes

## Screenshots (if applicable)

<!-- Add screenshots to help explain your changes. -->

## Breaking Changes

<!-- If this is a breaking change, describe: -->
- What breaks?
- Migration path for users
- Why is the breaking change necessary?

## Additional Notes

<!-- Any additional information for reviewers: -->
