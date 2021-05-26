.PHONY: setup
setup:
	pip install -r requirements-dev.txt
	pre-commit install
	pip install -e .

.PHONY: lint
lint: format
	mypy featurologists tests setup.py

.PHONY: format
format:
	pre-commit run --all-files --show-diff-on-failure

.PHONY: pytest
pytest:
	pytest tests

.PHONY: nbtest
nbtest:
	find notebooks -name '*.ipynb' -exec jupyter nbconvert --execute --inplace {} \;
	git status


.PHONY: nbclean
nbclean:
	find notebooks -name '*.ipynb' -exec nb-clean clean --remove-empty-cells {} \;
	git status
