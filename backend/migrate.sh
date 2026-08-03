#!/bin/bash

# Exit on error
set -e

# Export Flask app
export FLASK_APP=${FLASK_APP:-run.py}

# Derive PostgreSQL connection details from DATABASE_URL when present
if [ -n "$DATABASE_URL" ]; then
    DB_URL="$DATABASE_URL"
    DB_USERNAME=$(python - <<'PY'
import os, urllib.parse
url = urllib.parse.urlparse(os.environ.get('DATABASE_URL', ''))
print(url.username or '')
PY
)
    DB_PASSWORD=$(python - <<'PY'
import os, urllib.parse
url = urllib.parse.urlparse(os.environ.get('DATABASE_URL', ''))
print(url.password or '')
PY
)
    DB_HOST=$(python - <<'PY'
import os, urllib.parse
url = urllib.parse.urlparse(os.environ.get('DATABASE_URL', ''))
print(url.hostname or 'localhost')
PY
)
    DB_PORT=$(python - <<'PY'
import os, urllib.parse
url = urllib.parse.urlparse(os.environ.get('DATABASE_URL', ''))
print(url.port or 5432)
PY
)
    DB_NAME=$(python - <<'PY'
import os, urllib.parse
url = urllib.parse.urlparse(os.environ.get('DATABASE_URL', ''))
print(url.path.lstrip('/') or '')
PY
)

    export DB_USERNAME DB_PASSWORD DB_HOST DB_PORT DB_NAME
fi

echo "Running database migrations..."

# Check if migrations directory exists
if [ ! -d "migrations" ]; then
    echo "Initializing migrations directory..."
    flask db init
fi

# Try to upgrade first (in case there are existing migrations)
echo "Attempting to upgrade existing migrations..."
flask db upgrade || true

# Create and apply new migration if needed
echo "Creating new migration if needed..."
flask db migrate -m "Auto-generated migration" || true

echo "Applying migrations..."
flask db upgrade

echo "Checking if seed data is needed..."
python - <<'PY'
import os
from app import create_app
from app.models import db
from app.models.models import Topic

app = create_app()
with app.app_context():
    count = Topic.query.count()
    if count == 0:
        os.system('python seed_data.py')
    else:
        print('Database already contains data, skipping seed')
PY

echo "Database setup completed successfully!"