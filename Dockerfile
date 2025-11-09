FROM python:3.11-slim

# Avoids bytecode and ensures logs are sent to stdout
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Optional system dependencies (useful for psycopg, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project (for CI images; in dev, the bind-mount overwrites)
COPY . /app

# Default command can be overridden by docker-compose
CMD ["python", "ingest.py"]
