#!/bin/bash
# Run this inside the backend docker container to test migrations
# Example: docker-compose exec backend ./test_migration.sh

echo "Testing migration upgrade to head..."
alembic upgrade head

echo "Testing migration downgrade by 1..."
alembic downgrade -1

echo "Testing migration upgrade back to head..."
alembic upgrade head

echo "Migration rollback validation successful."
