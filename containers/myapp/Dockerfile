FROM python:3.9

RUN pip install --no-cache-dir boto3 fastapi uvicorn mlflow

WORKDIR /app

COPY webhook.py /app/webhook.py

EXPOSE 8000

CMD ["uvicorn", "webhook:app", "--host", "0.0.0.0", "--port", "8000"]
