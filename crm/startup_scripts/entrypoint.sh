#!/bin/sh

ls -l /app

if [ -f /app/startup_scripts/wait-for-it.sh ]; then
    echo "wait-for-it.sh found"
else
    echo "wait-for-it.sh not found"
    exit 1
fi

/app/startup_scripts/wait-for-it.sh db:5432 --strict --timeout=60 -- echo "Database is up"

if [ "$ENTRYPOINT_BACKEND" = 'true' ]; then
    echo "Starting Uvicorn... '$ENTRYPOINT_BACKEND'"
    alembic upgrade head
    
    if [ "$DEBUG" = "true" ]; then
        echo "DEBUG mode enabled - starting with reload"
        uvicorn main:app --host 0.0.0.0 --port 8000 --reload --proxy-headers
    else
        echo "Production mode - starting with 4 workers"
        uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4 --proxy-headers
    fi
else
    echo "No valid service specified. Check environment variables."
    echo "Available options: ENTRYPOINT_BACKEND"
    exit 1
fi

