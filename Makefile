.PHONY: validate test clean install docker-build docker-run

install:
	pip install -r requirements.txt
	pip install pytest

validate:
	python tooling/validate.py employee.md
	python tooling/validate.py examples/minimal.md
	python tooling/validate.py examples/ai-assistant.md
	python tooling/validate.py examples/data-analyst.md
	python tooling/validate.py examples/security-auditor.md
	python tooling/validate.py examples/senior-dev.md
	python tooling/validate.py examples/freelancer.md

test:
	pytest tests/

docker-build:
	docker build -t employee-validate .

docker-run:
	docker run --rm -v $(PWD):/app employee-validate employee.md

clean:
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf tests/__pycache__
	rm -rf tooling/__pycache__
