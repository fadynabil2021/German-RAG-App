#!/bin/bash
set -euo pipefail

echo "[entrypoint] Waiting for PostgreSQL..."
until python - <<EOF
import asyncpg, asyncio, os
async def check():
    conn = await asyncpg.connect(os.environ["DATABASE_URL"].replace("+asyncpg",""))
    await conn.close()
asyncio.run(check())
EOF
do
  echo "[entrypoint] DB not ready — retrying in 3s"; sleep 3
done

echo "[entrypoint] Running Alembic migrations..."
cd /app/models/db_schemes/minirag
alembic upgrade head
cd /app

exec "$@"
