from setuptools import find_packages, setup

setup(
    name="mlproject",
    version="0.1.0",
    author="Navyashree Byregowda",
    author_email="navyashreebyregowda@gmail.com",
    description="Modular, config-driven ML training and serving pipeline",
    packages=find_packages(exclude=["tests"]),
    python_requires=">=3.10",
    install_requires=[
        "pandas>=2.0", "numpy>=1.24", "scikit-learn>=1.4",
        "flask>=3.0", "pyyaml>=6.0", "joblib>=1.3",
    ],
)
