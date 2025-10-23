#!/bin/bash
set -e
cd /app

case "$1" in
  "worker")
    echo "🚀 Starting RQ Worker..."
    python -m worker.main
    ;;
  "api")
    echo "🌐 Starting FastAPI enqueue service..."
    uvicorn worker.api.enqueue_api:app --host 0.0.0.0 --port 8000
    ;;
  *)
    exec "$@"
    ;;
esac
