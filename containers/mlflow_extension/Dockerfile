FROM ghcr.io/mlflow/mlflow:v2.0.1

RUN pip install boto3 && pip install --upgrade mlflow

WORKDIR /app

COPY app.py /app/app.py
COPY setup.py /app/setup.py
RUN pip install .
