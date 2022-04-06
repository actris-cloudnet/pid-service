"""Package setup"""
from setuptools import find_packages, setup

setup(
    name="PID-SERVICE",
    install_requires=[
        "requests",
        "pydantic",
        "fastapi",
        "uvicorn",
    ],
    extras_require={
        "test": ["pytest", "pylint", "requests_mock", "mypy", "types-requests"],
        "dev": ["pre-commit"],
    },
    packages=find_packages(),
)
