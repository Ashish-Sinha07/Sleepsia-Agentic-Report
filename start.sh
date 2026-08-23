#!/bin/bash

# Sleepsia Agentic Reporting System - Start Script (Bash/Linux/Mac)
# Starts both backend and frontend

echo "=========================================="
echo "Sleepsia Agentic Reporting System"
echo "=========================================="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    exit 1
fi

# Check Node
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js is not installed"
    exit 1
fi

echo "✓ Python found: $(python3 --version)"
echo "✓ Node.js found: $(node --version)"
echo ""

# Setup Python environment
echo "Setting up Python environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

source .venv/bin/activate
pip install -r requirements.txt

# Start backend in background
echo ""
echo "Starting Backend (FastAPI) on http://localhost:8000..."
python -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Start the daily report scheduler. Email remains disabled unless explicitly enabled in .env.
python backend/scripts/start_report_scheduler.py &
SCHEDULER_PID=$!

# Wait for backend to start
sleep 3

# Start frontend
echo ""
echo "Starting Frontend (React + Vite) on http://localhost:3000..."
cd dashboard

if [ ! -d "node_modules" ]; then
    npm install
fi

npm run dev &
FRONTEND_PID=$!

echo ""
echo "=========================================="
echo "Sleepsia Agentic Reporting System Running"
echo "=========================================="
echo ""
echo "Frontend: http://localhost:3000"
echo "Backend:  http://localhost:8000"
echo "Scheduler: daily at configured report time"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for both processes
wait $BACKEND_PID $SCHEDULER_PID $FRONTEND_PID
