FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8080

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

# Cloud Run injects PORT. --timeout 0 disables gunicorn's own timeout
# since Cloud Run already enforces a request timeout.
CMD exec gunicorn --workers 2 --threads 8 --timeout 0 --bind :${PORT} app:app
