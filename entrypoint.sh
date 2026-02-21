#!/bin/sh

# 1. Wait for PostgreSQL to be ready
# This uses a pure Python loop to check the connection without extra tools
echo "Waiting for database (db:5432)..."
python << END
import socket
import time
import sys

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
while True:
    try:
        s.connect(('db', 5432))
        s.close()
        break
    except socket.error:
        time.sleep(0.5)
END

echo "PostgreSQL is ready!"

# 2. Run Alembic migrations
# This automatically creates all tables and the 'sentiment' column
echo "Syncing database schema..."
alembic upgrade head

# 3. Start the FastAPI server
echo "Starting LuminaLib API..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000