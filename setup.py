from setuptools import find_packages, setup


setup(
    name="featurologists",
    version="0.0.1",
    python_requires=">=3.6.0",
    url="https://github.com/geewynn/Featurologists",
    packages=find_packages(),
    install_requires=[
        "customer-segmentation-toolkit>=0.0.2",
    ],
)
