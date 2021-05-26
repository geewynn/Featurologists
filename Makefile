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

.PHONY: test-py
test-py:
	pytest tests

.PHONY: test-nb
test-nb:
	find notebooks -name '*.ipynb' -exec jupyter nbconvert --execute --inplace {} \;
	git status


.PHONY: clean-nb
clean-nb:
	find notebooks -name '*.ipynb' -exec nb-clean clean --remove-empty-cells {} \;
	git status
