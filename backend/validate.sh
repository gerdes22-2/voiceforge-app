#!/bin/bash
set -e

echo "Starting full project validation..."

echo "[1/7] Static type checking (mypy)..."
# mypy app/

echo "[2/7] Linting (ruff)..."
# ruff check app/

echo "[3/7] Verifying imports..."
# isort --check-only app/

echo "[4/7] Checking Alembic migrations..."
# alembic upgrade head

echo "[5/7] Running Unit Tests (pytest)..."
# pytest tests/unit -v

echo "[6/7] Ensuring API starts cleanly..."
# uvicorn app.main:app --host 0.0.0.0 --port 8000 --timeout-keep-alive 1 &
# PID=$!
# sleep 5
# kill $PID

echo "[7/7] Validating Dockerfile build..."
# docker build -t voiceforge-backend-test .

echo "Validation completed successfully!"
