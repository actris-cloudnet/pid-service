FROM python:3 AS base

WORKDIR /app

COPY . /app

RUN pip3 install --upgrade pip
RUN pip3 install .

FROM base AS prod
CMD ["scripts/run-api.py"]
