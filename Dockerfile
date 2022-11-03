FROM python:3 AS base

EXPOSE 5800

WORKDIR /app

COPY setup.py .
RUN pip3 install --upgrade pip
RUN pip3 install .

FROM base AS dev
RUN pip3 install -e .[test]
CMD ["uvicorn", "pid_service.main:app", "--reload", "--host", "0.0.0.0", "--port", "5800"]

FROM base AS prod
COPY . .
RUN pip3 install .
CMD ["uvicorn", "pid_service.main:app", "--host", "0.0.0.0", "--port", "5800"]
