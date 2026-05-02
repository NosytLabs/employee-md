.PHONY: validate validate-strict test lint format format-check typecheck clean install ci docker-build docker-run tailwind

install:
	pip install -e .
	pip install -e .[dev]

# Permissive validation via the CLI (matches the runtime contract surface)
validate:
	python -m tooling.cli employee.md
	python -m tooling.cli examples/minimal.md
	python -m tooling.cli examples/senior-dev.md
	python -m tooling.cli examples/ai-assistant.md
	python -m tooling.cli examples/data-analyst.md
	python -m tooling.cli examples/security-auditor.md
	python -m tooling.cli examples/freelancer.md
	python -m tooling.cli examples/devops-engineer.md
	python -m tooling.cli examples/product-manager.md
	python -m tooling.cli examples/zhc-worker.md
	python -m tooling.cli examples/trading-bot.md

# Strict JSON Schema validation. molt-bot-integration.md is a markdown guide
# with embedded YAML and is intentionally excluded.
validate-strict:
	python tooling/strict_schema_check.py

test:
	python -m pytest tests/ -v

# NOTE: CI only lints/formats `tooling/` (not `tests/`). Keep these targets
# aligned with `.github/workflows/validate.yml` so `make ci` is a faithful
# local mirror -- do not silently expand scope.
lint:
	ruff check tooling/

format:
	ruff format tooling/

format-check:
	ruff format --check tooling/

typecheck:
	mypy tooling/ --ignore-missing-imports --show-error-codes

# Run the full quality gate (mirrors CI)
ci: lint format-check typecheck test validate validate-strict

docker-build:
	docker build -t employee-validate .

docker-run:
	docker run --rm -v $(PWD):/app employee-validate employee.md

clean:
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf tests/__pycache__
	rm -rf tooling/__pycache__

# Regenerate web/static/tailwind.css from the templates using the pinned
# standalone Tailwind CLI binary (no Node required). Auto-downloads the
# v3.4.17 standalone binary into .local/bin/ on first run, then rebuilds.
# Run this whenever you add or change Tailwind utility classes in a template.
TAILWIND_VERSION := v3.4.17
TAILWIND_BIN := .local/bin/tailwindcss
# SHA256 of the linux-x64 binary published in
# https://github.com/tailwindlabs/tailwindcss/releases/download/v3.4.17/sha256sums.txt
# Pinned so the post-merge hook (and any contributor) can never silently
# pull a tampered binary — the download is rejected if it doesn't match.
TAILWIND_SHA256 := 7d24f7fa191d2193b78cd5f5a42a6093e14409521908529f42d80b11fde1f1d4
tailwind:
	@if [ ! -x $(TAILWIND_BIN) ]; then \
		mkdir -p .local/bin; \
		echo "Downloading standalone Tailwind CLI $(TAILWIND_VERSION)..."; \
		curl -sSL -o $(TAILWIND_BIN).tmp "https://github.com/tailwindlabs/tailwindcss/releases/download/$(TAILWIND_VERSION)/tailwindcss-linux-x64"; \
		echo "$(TAILWIND_SHA256)  $(TAILWIND_BIN).tmp" | sha256sum -c - || { rm -f $(TAILWIND_BIN).tmp; echo "Tailwind binary checksum FAILED — refusing to install"; exit 1; }; \
		mv $(TAILWIND_BIN).tmp $(TAILWIND_BIN); \
		chmod +x $(TAILWIND_BIN); \
	fi
	$(TAILWIND_BIN) -c tailwind.config.js -i web/static/tailwind.src.css -o web/static/tailwind.css --minify
