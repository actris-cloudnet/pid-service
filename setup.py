"""Package setup"""
from setuptools import find_packages, setup

setup(
    name="PID-SERVICE",
    version="1.1.1",
    install_requires=[
        "requests>=2.31.0,<2.32.0",
        "pydantic>=2.0.0,<3.0.0",
        "pydantic-settings>=2.0.0,<3.0.0",
        "fastapi>=0.100.0,<0.101.0",
        "uvicorn>=0.23.0,<0.24.0",
    ],
    extras_require={
        "test": [
            "pytest",
            "pylint",
            "mypy",
            "requests_mock>=1.11.0,<1.12.0",
            "types-requests>=2.31.0,<2.32.0",
        ],
        "dev": ["pre-commit", "release-version"],
    },
    packages=find_packages(),
)
