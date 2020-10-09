from setuptools import setup, find_packages

setup(name="PID-SERVICE",
      install_requires=['requests',
                        'pytest',
                        'pylint',
                        'pydantic',
                        'requests_mock',
                        'fastapi',
                        'uvicorn',
                        ],
      packages=find_packages())
