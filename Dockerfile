FROM python:3 AS base

WORKDIR /app

COPY setup.py .
RUN pip3 install --upgrade pip
RUN pip3 install .

FROM base AS dev
RUN pip3 install -e .[test]
CMD ["scripts/run-api.py"]

FROM base AS prod
COPY . .
RUN pip3 install .
CMD ["scripts/run-api.py"]
