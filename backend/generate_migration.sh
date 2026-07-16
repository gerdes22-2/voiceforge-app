#!/bin/bash
# Run this inside the backend docker container to auto-generate migrations
# Example: docker-compose exec backend ./generate_migration.sh "Initial schema"

MESSAGE=${1:-"Initial schema"}
alembic revision --autogenerate -m "$MESSAGE"
