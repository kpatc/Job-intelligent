#!/bin/bash
set -e

echo "=== Superset Initialization ==="

# Install database drivers
echo "0. Installing database drivers..."
pip install -q snowflake-sqlalchemy 2>/dev/null || true

# Database migrations
echo "1. Running database migrations..."
superset db upgrade

# Create admin user
echo "2. Creating admin user..."
superset fab create-admin \
    --username admin \
    --firstname Admin \
    --lastname User \
    --email admin@superset.com \
    --password admin123 || echo "Admin user may already exist"

# Initialize role permissions
echo "3. Initializing permissions..."
superset init

# Load examples (optional, can be skipped for production)
echo "4. Loading example dashboards..."
superset load_examples || echo "Examples loading skipped or already loaded"

# Start Superset
echo "5. Starting Superset application..."
exec superset run -h 0.0.0.0 -p 8088 --with-threads --reload --debugger
