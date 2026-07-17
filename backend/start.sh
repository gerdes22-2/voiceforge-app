#!/bin/bash
# Make sure python can find the worker and shared modules
export PYTHONPATH=/app:$PYTHONPATH

# Start Celery worker in the background
cd /app/worker
celery -A tasks.celery_app worker --loglevel=info &

# Start FastAPI in the foreground
cd /app/backend
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
