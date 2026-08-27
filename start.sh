#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "Starting FastAPI backend internally on port 8000..."
cd /app/backend
# Bind to 127.0.0.1 since FastAPI is only accessed internally by Next.js proxy
uv run uvicorn main:app --host 127.0.0.1 --port 8000 &

echo "Waiting for FastAPI to be ready..."
for i in {1..30}; do
  if curl -s http://127.0.0.1:8000/health > /dev/null 2>&1; then
    echo "FastAPI is ready!"
    break
  fi
  sleep 1
done

echo "Starting Next.js frontend publicly on port 7860..."
cd /app/frontend
# Explicitly set the backend URL for the Next.js proxy rewrite
export BACKEND_API_URL=http://127.0.0.1:8000
npm run start -- -p 7860
