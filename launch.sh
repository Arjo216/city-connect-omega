#!/bin/bash

echo "🚀 KILLING OLD PROCESSES..."
fuser -k 8000/tcp 2>/dev/null
fuser -k 8501/tcp 2>/dev/null

echo "🧠 STARTING BACKEND (API & ML)..."
uvicorn api_server:app --port 8000 > backend.log 2>&1 &

echo "🖥️  STARTING FRONTEND (DASHBOARD)..."
streamlit run dashboard.py --server.port 8501