#!/bin/bash
# Runs after a task is merged into main. Idempotent. Stdin is closed.
#
# Why this exists:
#  - Tailwind is now prebuilt into web/static/tailwind.css (Task #6 removed
#    the CDN). The build is driven by tailwind.config.js scanning
#    web/templates/**/*.html. When a merged task adds new template files or
#    new utility classes, the prebuilt CSS goes out of date and the live
#    site renders without those styles. Rebuilding here keeps main green.
#  - `make tailwind` is itself idempotent: it auto-downloads the pinned
#    standalone Tailwind CLI on first run, then rebuilds the minified CSS.
set -euo pipefail

# Re-install the package in editable mode so any new dependencies declared
# by the merged task land on PYTHONPATH before workflows restart. `--quiet`
# keeps the log noise down; `pip install -e .` is fast on a warm cache.
if [ -f pyproject.toml ]; then
  python -m pip install --quiet -e . || true
fi

# Always rebuild Tailwind. This is a no-op (~4s) if no template/CSS changed,
# and the only thing that prevents broken styling when templates do change.
if [ -f tailwind.config.js ] && [ -f Makefile ]; then
  make tailwind
fi

echo "post-merge: ok"
