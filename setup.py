from setuptools import setup, find_packages

setup(name="PID-SERVICE",
      install_requires=['requests',
                        'pydantic',
                        'fastapi',
                        'uvicorn',
                        ],
      extras_require={'test': ['pytest',
                               'pylint',
                               'requests_mock',
                               'mypy',
                               'types-requests']},
      packages=find_packages())
