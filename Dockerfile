FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY input ./input
COPY output ./output

ENTRYPOINT ["python", "-m", "app.main", "--input", "/app/input", "--output", "/app/output"]
