#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "Starting FastAPI backend internally on port 8000..."
cd /app/backend
# Run uvicorn in the background (&)
uvicorn main:app --host 127.0.0.1 --port 8000 &

echo "Starting Next.js frontend publicly on port 7860..."
cd /app/frontend
# Run Next.js in the foreground (blocks the script from exiting)
npm run start -- -p 7860
