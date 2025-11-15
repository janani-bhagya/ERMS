#!/bin/bash

# Emergency Room Management System - Quick Start Script

echo "=================================="
echo "Emergency Room Management System"
echo "=================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed. Please install Python 3.9+${NC}"
    exit 1
fi

# Check if Node is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}Node.js is not installed. Please install Node.js 18+${NC}"
    exit 1
fi

echo -e "${BLUE}Step 1: Setting up Backend...${NC}"
cd backend

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -q -r requirements.txt

# Initialize database
echo "Initializing database..."
python -m app.init_db

echo -e "${GREEN}✓ Backend setup complete${NC}"
echo ""

echo -e "${BLUE}Step 2: Setting up Frontend...${NC}"
cd ../frontend

# Install dependencies
if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install
else
    echo "Node modules already installed"
fi

echo -e "${GREEN}✓ Frontend setup complete${NC}"
echo ""

echo "=================================="
echo "Starting Servers..."
echo "=================================="
echo ""

# Start backend in background
echo -e "${BLUE}Starting Backend Server on http://localhost:8000${NC}"
cd ../backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Wait for backend to start
sleep 5

# Start frontend
echo -e "${BLUE}Starting Frontend Server on http://localhost:3000${NC}"
cd ../frontend
npm run dev &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

echo ""
echo "=================================="
echo -e "${GREEN}✓ Servers are running!${NC}"
echo "=================================="
echo ""
echo "Backend API:  http://localhost:8000"
echo "API Docs:     http://localhost:8000/docs"
echo "WebSocket:    http://localhost:8000/ws"
echo "Frontend:     http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Shutting down servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "Servers stopped"
    exit 0
}

# Trap Ctrl+C
trap cleanup INT

# Wait for processes
wait

sdf