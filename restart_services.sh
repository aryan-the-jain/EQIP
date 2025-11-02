#!/bin/bash

# Eqip.ai Services Restart Script
# This script kills existing backend and Streamlit processes and starts them fresh

echo "🔄 Restarting Eqip.ai Services..."
echo "=================================="

# Change to project directory
cd "$(dirname "$0")"
PROJECT_DIR=$(pwd)
echo "📁 Working directory: $PROJECT_DIR"

# Activate virtual environment
echo "🐍 Activating virtual environment..."
source venv/bin/activate

# Kill existing processes
echo "🛑 Stopping existing services..."

# Kill FastAPI backend processes
echo "   - Stopping FastAPI backend..."
pkill -f "uvicorn backend.main:app" 2>/dev/null || echo "   - No FastAPI processes found"

# Kill Streamlit processes
echo "   - Stopping Streamlit..."
pkill -f "streamlit run" 2>/dev/null || echo "   - No Streamlit processes found"

# Wait a moment for processes to fully terminate
sleep 2

# Check if ports are free
echo "🔍 Checking ports..."
if lsof -i :8000 >/dev/null 2>&1; then
    echo "   ⚠️  Port 8000 still in use, force killing..."
    lsof -ti :8000 | xargs kill -9 2>/dev/null || true
fi

if lsof -i :8501 >/dev/null 2>&1; then
    echo "   ⚠️  Port 8501 still in use, force killing..."
    lsof -ti :8501 | xargs kill -9 2>/dev/null || true
fi

sleep 1

# Start FastAPI backend
echo "🚀 Starting FastAPI backend on port 8000..."
nohup uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000 > logs/backend.log 2>&1 &
BACKEND_PID=$!
echo "   - Backend PID: $BACKEND_PID"

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
for i in {1..10}; do
    if curl -s http://localhost:8000/v1/health >/dev/null 2>&1; then
        echo "   ✅ Backend is ready!"
        break
    fi
    echo "   - Attempt $i/10..."
    sleep 2
done

# Check if backend started successfully
if ! curl -s http://localhost:8000/v1/health >/dev/null 2>&1; then
    echo "   ❌ Backend failed to start. Check logs/backend.log"
    exit 1
fi

# Start Streamlit enhanced app
echo "🎨 Starting Enhanced Streamlit app on port 8501..."
nohup streamlit run frontend/streamlit_app_enhanced.py --server.port 8501 --server.headless true > logs/streamlit.log 2>&1 &
STREAMLIT_PID=$!
echo "   - Streamlit PID: $STREAMLIT_PID"

# Wait for Streamlit to start
echo "⏳ Waiting for Streamlit to start..."
for i in {1..15}; do
    if curl -s http://localhost:8501 >/dev/null 2>&1; then
        echo "   ✅ Streamlit is ready!"
        break
    fi
    echo "   - Attempt $i/15..."
    sleep 2
done

# Check if Streamlit started successfully
if ! curl -s http://localhost:8501 >/dev/null 2>&1; then
    echo "   ❌ Streamlit failed to start. Check logs/streamlit.log"
    exit 1
fi

# Save PIDs for future reference
echo "$BACKEND_PID" > .backend.pid
echo "$STREAMLIT_PID" > .streamlit.pid

echo ""
echo "🎉 All services started successfully!"
echo "=================================="
echo "📊 FastAPI Backend:    http://localhost:8000"
echo "📋 API Documentation:  http://localhost:8000/docs"
echo "🎨 Enhanced Streamlit: http://localhost:8501"
echo ""
echo "📝 Logs:"
echo "   - Backend:  logs/backend.log"
echo "   - Streamlit: logs/streamlit.log"
echo ""
echo "🛑 To stop services: ./stop_services.sh"
echo "📊 To check status:  ./check_services.sh"
echo ""
echo "✨ Ready to use your complete IP lifecycle pipeline!"
