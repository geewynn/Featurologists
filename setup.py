from setuptools import find_packages, setup


setup(
    name="featurologists",
    version="0.0.1",
    python_requires=">=3.6.0",
    url="https://github.com/geewynn/Featurologists",
    packages=find_packages(),
    install_requires=[
        "customer-segmentation-toolkit>=0.0.2",
        "xgboost>=1.4.2",
        "lightgbm>=3.2.1",
        "scikit-learn>=0.24.2",
        "numpy>=1.20.3",
        "matplotlib>=3.4.2",
        "pandas>=1.2.4",
        "kafka-python>=2.0.2",
        "tqdm>=4.61.0",
        "typer>=0.3.2",
    ],
    entry_points={
        "console_scripts": ["featurologists=featurologists.app:app"],
    },
)
