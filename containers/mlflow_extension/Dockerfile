# FROM ghcr.io/mlflow/mlflow:v2.0.1
FROM ghcr.io/mlflow/mlflow:latest

WORKDIR /app
RUN pip install boto3 && pip install --upgrade mlflow
RUN pip install psycopg2-binary

COPY app.py /app/app.py
COPY setup.py /app/setup.py
# COPY mlflow_patch /app/mlflow_patch
RUN pip3 install .  # setup.py を実行する

# COPY patch.py /app/patch.py
# RUN mkdir -p $(python -m site --user-site) && cp patch.py $(python -m site --user-site)/usercustomize.py  # patch を適用する
