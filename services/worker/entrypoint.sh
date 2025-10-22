#!/bin/bash
set -e

cd /app
export PYTHONPATH=/app

if [ "$1" = "worker" ]; then
    echo "🚀 Starting RQ Worker..."
    exec python -m main
elif [ "$1" = "api" ]; then
    echo "🌐 Starting FastAPI enqueue service..."
    exec uvicorn api.enqueue_api:app --host 0.0.0.0 --port 8000
else
    echo "⚙️ Running custom command: $@"
    exec "$@"
fi
