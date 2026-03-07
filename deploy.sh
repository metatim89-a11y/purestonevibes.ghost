#!/bin/bash

# --- Pure Stone Vibes Self-Hosted Deployment (VENV Mode) ---

echo "--- STARTING PURE STONE VIBES (FastAPI) ---"

# 1. Kill any existing uvicorn processes on port 8000
echo "Cleaning up existing processes on port 8000..."
fuser -k 8000/tcp > /dev/null 2>&1

# 2. Check for VENV and create if missing
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating..."
    python3 -m venv venv
    ./venv/bin/pip install -r requirements.txt
fi

# 3. Launch the server in the background
echo "Launching FastAPI server..."
nohup ./venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 > server.log 2>&1 &

echo "--- DEPLOYMENT COMPLETE ---"
echo "Log file: server.log"
echo "Visit: http://localhost:8000"
