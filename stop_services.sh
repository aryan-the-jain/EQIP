#!/bin/bash

# Eqip.ai Services Stop Script
# This script gracefully stops all backend and Streamlit processes

echo "🛑 Stopping Eqip.ai Services..."
echo "==============================="

# Change to project directory
cd "$(dirname "$0")"

# Stop services using saved PIDs if available
if [ -f ".backend.pid" ]; then
    BACKEND_PID=$(cat .backend.pid)
    echo "🔌 Stopping FastAPI backend (PID: $BACKEND_PID)..."
    kill $BACKEND_PID 2>/dev/null || echo "   - Process already stopped"
    rm -f .backend.pid
fi

if [ -f ".streamlit.pid" ]; then
    STREAMLIT_PID=$(cat .streamlit.pid)
    echo "🎨 Stopping Streamlit (PID: $STREAMLIT_PID)..."
    kill $STREAMLIT_PID 2>/dev/null || echo "   - Process already stopped"
    rm -f .streamlit.pid
fi

# Kill any remaining processes
echo "🧹 Cleaning up remaining processes..."
pkill -f "uvicorn backend.main:app" 2>/dev/null || echo "   - No FastAPI processes found"
pkill -f "streamlit run" 2>/dev/null || echo "   - No Streamlit processes found"

# Force kill if ports are still in use
if lsof -i :8000 >/dev/null 2>&1; then
    echo "   🔨 Force killing processes on port 8000..."
    lsof -ti :8000 | xargs kill -9 2>/dev/null || true
fi

if lsof -i :8501 >/dev/null 2>&1; then
    echo "   🔨 Force killing processes on port 8501..."
    lsof -ti :8501 | xargs kill -9 2>/dev/null || true
fi

sleep 2

# Verify ports are free
echo "🔍 Verifying ports are free..."
if ! lsof -i :8000 >/dev/null 2>&1 && ! lsof -i :8501 >/dev/null 2>&1; then
    echo "✅ All services stopped successfully!"
    echo "   - Port 8000: Free"
    echo "   - Port 8501: Free"
else
    echo "⚠️  Some ports may still be in use"
    echo "   - Port 8000: $(lsof -i :8000 >/dev/null 2>&1 && echo 'In use' || echo 'Free')"
    echo "   - Port 8501: $(lsof -i :8501 >/dev/null 2>&1 && echo 'In use' || echo 'Free')"
fi

echo ""
echo "🚀 To restart services: ./restart_services.sh"
