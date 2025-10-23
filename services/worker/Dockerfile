FROM python:3.11-slim AS base

WORKDIR /app
COPY . /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ libpq-dev curl && rm -rf /var/lib/apt/lists/*

# Install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install the worker package in editable mode (for live reload)
RUN pip install -e .

# Entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
