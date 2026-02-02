.PHONY: validate test clean install docker-build docker-run

install:
	pip install -e .
	pip install -e .[dev]

validate:
	python -m tooling.cli employee.md
	python -m tooling.cli examples/minimal.md
	python -m tooling.cli examples/ai-assistant.md
	python -m tooling.cli examples/data-analyst.md
	python -m tooling.cli examples/security-auditor.md
	python -m tooling.cli examples/senior-dev.md
	python -m tooling.cli examples/freelancer.md

test:
	python -m pytest tests/

docker-build:
	docker build -t employee-validate .

docker-run:
	docker run --rm -v $(PWD):/app employee-validate employee.md

clean:
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf tests/__pycache__
	rm -rf tooling/__pycache__
