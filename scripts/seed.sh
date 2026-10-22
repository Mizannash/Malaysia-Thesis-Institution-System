#!/usr/bin/env sh
set -e

echo "==> [MTIS Seeder] Checking database readiness..."
python -c "
import time, socket, os
from urllib.parse import urlparse

url = os.getenv('DATABASE_URL', '')
if url.startswith('postgresql'):
    parsed = urlparse(url)
    host = parsed.hostname or 'localhost'
    port = parsed.port or 5432
    for attempt in range(30):
        try:
            with socket.create_connection((host, port), timeout=2):
                print(f'==> [MTIS Seeder] Connected to database at {host}:{port}')
                break
        except Exception:
            time.sleep(1)
" || true

echo "==> [MTIS Seeder] Running migrations and idempotent seeding..."
if [ -f "/app/scripts/seed.py" ]; then
    python /app/scripts/seed.py
elif [ -f "scripts/seed.py" ]; then
    python scripts/seed.py
else
    python -m scripts.seed
fi

echo "==> [MTIS Seeder] Database ready with demo accounts (student@demo.test, supervisor@demo.test)."

# Execute any trailing entrypoint command
if [ "$#" -gt 0 ]; then
    exec "$@"
fi
