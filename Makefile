.PHONY: setup
setup:
	pip install -r requirements-dev.txt
	pre-commit install

.PHONY: lint
lint: format
	mypy featurologists tests setup.py

.PHONY: format
format:
	pre-commit run --all-files --show-diff-on-failure

.PHONY: test
test: lint
	pytest tests
	find notebooks -name '*.ipynb' -exec jupyter nbconvert --execute --inplace {} \;
