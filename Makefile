.PHONY: validate test clean install

install:
	pip install -r requirements.txt

validate:
	python tooling/validate.py employee.md
	python tooling/validate.py examples/minimal.md
	python tooling/validate.py examples/ai-assistant.md
	python tooling/validate.py examples/data-analyst.md
	python tooling/validate.py examples/security-auditor.md
	python tooling/validate.py examples/senior-dev.md
	python tooling/validate.py examples/freelancer.md

test: validate

clean:
	rm -rf __pycache__
	rm -rf .pytest_cache
