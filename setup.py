from setuptools import find_packages, setup


TOOLKIT_BRANCH = (
    "allow-build-mini-batch"  # Artem Y: I'm currently working in this branch.
)

setup(
    name="featurologists",
    version="0.0.1",
    python_requires=">=3.6.0",
    url="https://github.com/geewynn/Featurologists",
    packages=find_packages(),
    install_requires=[
        # "customer-segmentation-toolkit>=0.0.2",
        f"customer-segmentation-toolkit @ https://github.com/artemlops/customer-segmentation-toolkit/archive/{TOOLKIT_BRANCH}.zip",  # noqa
        "xgboost>=1.4.2",
        "lightgbm>=3.2.1",
        "scikit-learn>=0.24.2",
        "numpy>=1.20.3",
        "matplotlib>=3.4.2",
        "pandas>=1.2.4",
        "kafka-python>=2.0.2",
        "typer>=0.3.2",
        "feast==0.10.7",
    ],
    entry_points={
        "console_scripts": ["featurologists=featurologists.app:app"],
    },
)
