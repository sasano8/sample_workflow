FROM python:3.12

WORKDIR /build

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY data/ /app/data/

WORKDIR /app
COPY loader.py loader.py

CMD ["python3", "loader.py"]
