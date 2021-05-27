# Featurologists

Main repository for the [MLOps Engineering Lab #2](https://github.com/mlopscommunity/engineering.labs/tree/master/Lab2_Feature_Store_for_ML) "Feature Store for ML" by Team #2.

### Quickstart
```bash
# Create a virtual environemnt:
python -m venv ./venv
source venv/bin/activate

# Create a jupyter kernel in current virtualenv for local development:
python -m ipykernel install --user --name=featurologists

# Setup project:
make setup    # installs package, linters, pre-commit hooks
make lint     # beautifies the staged code
make pytest   # runs tests from ./tests/
make nbtest   # executes notebooks from ./notebooks
make nbclean  # cleans outputs in notebooks from ./notebooks
```

NB: `pre-commit` hooks installed to your system might be very annoying not allowing you to commit your code.
If you're pissed off, please do `git commit -m "I'm pissed off" --no-verify` and push your changes, we'll figure this out.


### Repository format

1. Primary python code:
```
$ tree featurologists
featurologists
├── __init__.py
└── models
    ├── customer_segmentation
    │   └── __init__.py
    └── __init__.py
```

If you need to add a pip dependency, please add it to [setup.py](setup.py) (section `install_requires`).
Development requirements (linters, jupyters, etc) can be added to [requirements-dev.txt](requirements-dev.txt).


2. Checking your code in jupyter notebooks:
```
$ tree notebooks
notebooks
└── models
    ├── country_prediction
    └── customer_segmentation
```
Please don't keep any important code in jupyter notebooks as it can't be versioned or re-used.
It's better to import python code via `import featurologists` in the notebooks and test it.
