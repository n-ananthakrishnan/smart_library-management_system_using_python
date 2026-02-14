#!/bin/bash

set -e

echo "Django startup script"

# Try to run migrations (will timeout if DB not ready, but that's OK - retry on restart)
echo "Attempting Django migrations..."
timeout 30 python manage.py migrate --noinput || echo "⚠️ Migration timed out or failed - will retry on next container start"

echo "Collecting static files..."
timeout 30 python manage.py collectstatic --noinput --clear || true

echo "Starting application..."

# Execute the main command  
exec "$@"
