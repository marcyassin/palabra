#!/bin/bash
set -e

if [ "$1" = "worker" ]; then
    echo "🚀 Starting RQ Worker..."
    exec python -m worker.main
elif [ "$1" = "api" ]; then
    echo "🌐 Starting FastAPI enqueue service..."
    exec uvicorn worker.api.enqueue_api:app --host 0.0.0.0 --port 8000
else
    echo "⚙️ Running custom command: $@"
    exec "$@"
fi
