.PHONY: setup
setup:
	pip install -r requirements-dev.txt
	python -m ipykernel install --user --name=featurologists
	pre-commit install
	pip install -e .

.PHONY: lint
lint:
	pre-commit run --all-files --show-diff-on-failure

.PHONY: test
test: pytest nbtest

.PHONY: pytest
pytest:
	pytest tests

.PHONY: nbtest
nbtest:
	python notebooks/run_tests.py

.PHONY: nbclean
nbclean:
	find notebooks -name '*.ipynb' -exec nb-clean clean --remove-empty-cells {} \;

include deploy.mk
