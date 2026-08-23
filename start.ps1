# Sleepsia Agentic Reporting System - Start Script (PowerShell)
# Starts both backend and frontend

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Sleepsia Agentic Reporting System" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
try {
    python --version 2>$null
    $pythonInstalled = $true
} catch {
    $pythonInstalled = $false
}

# Check if Node is installed
try {
    node --version 2>$null
    $nodeInstalled = $true
} catch {
    $nodeInstalled = $false
}

if (-not $pythonInstalled) {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

if (-not $nodeInstalled) {
    Write-Host "ERROR: Node.js is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Python found: $(python --version)" -ForegroundColor Green
Write-Host "✓ Node.js found: $(node --version)" -ForegroundColor Green
Write-Host ""

# Start backend
Write-Host "Starting Backend (FastAPI)..." -ForegroundColor Cyan
Write-Host "Backend will run on: http://localhost:8000" -ForegroundColor Yellow
Write-Host ""

# Activate venv if it exists
if (Test-Path ".\.venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Gray
    & ".\.venv\Scripts\Activate.ps1"
} else {
    Write-Host "Creating virtual environment..." -ForegroundColor Gray
    python -m venv .venv
    & ".\.venv\Scripts\Activate.ps1"
    Write-Host "Installing Python dependencies..." -ForegroundColor Gray
    pip install -r requirements.txt
}

# Start backend in a separate window
Write-Host "Launching backend server..." -ForegroundColor Gray
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; python -m uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000"

# Wait a moment for backend to start
Start-Sleep -Seconds 3

# Start frontend
Write-Host ""
Write-Host "Starting Frontend (React + Vite)..." -ForegroundColor Cyan
Write-Host "Frontend will run on: http://localhost:5173" -ForegroundColor Yellow
Write-Host ""

cd dashboard

# Install dependencies if needed
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing Node.js dependencies..." -ForegroundColor Gray
    npm install
}

# Start frontend
Write-Host "Launching frontend development server..." -ForegroundColor Gray
npm run dev

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Sleepsia Agentic Reporting System Started" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Frontend: http://localhost:5173" -ForegroundColor Green
Write-Host "Backend:  http://localhost:8000" -ForegroundColor Green
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""
