#!/bin/bash
# Make sure python can find the worker and shared modules
# If we are in /app (Docker), use that, otherwise use current directory
export PYTHONPATH=${PWD}:/app:$PYTHONPATH

# Start Celery worker in the background
cd ../worker || cd /app/worker
celery -A tasks.celery_app worker --loglevel=info &

# Start FastAPI in the foreground
cd ../backend || cd /app/backend
python3 create_tables.py
alembic upgrade head || true
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
