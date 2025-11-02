#!/bin/bash

# Eqip.ai Services Status Check Script
# This script checks the status of all services and provides useful information

echo "📊 Eqip.ai Services Status"
echo "=========================="

# Change to project directory
cd "$(dirname "$0")"

# Check FastAPI Backend
echo "🔧 FastAPI Backend (Port 8000):"
if curl -s http://localhost:8000/v1/health >/dev/null 2>&1; then
    HEALTH_STATUS=$(curl -s http://localhost:8000/v1/health | jq -r '.status' 2>/dev/null || echo "ok")
    echo "   ✅ Status: Running ($HEALTH_STATUS)"
    echo "   🌐 URL: http://localhost:8000"
    echo "   📋 Docs: http://localhost:8000/docs"
else
    echo "   ❌ Status: Not running"
fi

# Check Streamlit
echo ""
echo "🎨 Streamlit Enhanced App (Port 8501):"
if curl -s http://localhost:8501 >/dev/null 2>&1; then
    echo "   ✅ Status: Running"
    echo "   🌐 URL: http://localhost:8501"
else
    echo "   ❌ Status: Not running"
fi

# Check processes
echo ""
echo "🔍 Process Information:"
BACKEND_PROCESSES=$(ps aux | grep -E "uvicorn.*backend\.main" | grep -v grep | wc -l | tr -d ' ')
STREAMLIT_PROCESSES=$(ps aux | grep -E "streamlit run" | grep -v grep | wc -l | tr -d ' ')

echo "   - FastAPI processes: $BACKEND_PROCESSES"
echo "   - Streamlit processes: $STREAMLIT_PROCESSES"

if [ "$BACKEND_PROCESSES" -gt 0 ]; then
    echo "   - Backend PIDs: $(ps aux | grep -E "uvicorn.*backend\.main" | grep -v grep | awk '{print $2}' | tr '\n' ' ')"
fi

if [ "$STREAMLIT_PROCESSES" -gt 0 ]; then
    echo "   - Streamlit PIDs: $(ps aux | grep -E "streamlit run" | grep -v grep | awk '{print $2}' | tr '\n' ' ')"
fi

# Check ports
echo ""
echo "🔌 Port Status:"
echo "   - Port 8000: $(lsof -i :8000 >/dev/null 2>&1 && echo 'In use' || echo 'Free')"
echo "   - Port 8501: $(lsof -i :8501 >/dev/null 2>&1 && echo 'In use' || echo 'Free')"

# Check log files
echo ""
echo "📝 Log Files:"
if [ -f "logs/backend.log" ]; then
    BACKEND_LOG_SIZE=$(wc -l < logs/backend.log 2>/dev/null || echo "0")
    echo "   - Backend log: logs/backend.log ($BACKEND_LOG_SIZE lines)"
    if [ "$BACKEND_LOG_SIZE" -gt 0 ]; then
        echo "     Last entry: $(tail -1 logs/backend.log 2>/dev/null | cut -c1-80)..."
    fi
else
    echo "   - Backend log: Not found"
fi

if [ -f "logs/streamlit.log" ]; then
    STREAMLIT_LOG_SIZE=$(wc -l < logs/streamlit.log 2>/dev/null || echo "0")
    echo "   - Streamlit log: logs/streamlit.log ($STREAMLIT_LOG_SIZE lines)"
    if [ "$STREAMLIT_LOG_SIZE" -gt 0 ]; then
        echo "     Last entry: $(tail -1 logs/streamlit.log 2>/dev/null | cut -c1-80)..."
    fi
else
    echo "   - Streamlit log: Not found"
fi

# Overall status
echo ""
echo "📋 Overall Status:"
if curl -s http://localhost:8000/v1/health >/dev/null 2>&1 && curl -s http://localhost:8501 >/dev/null 2>&1; then
    echo "   🎉 All services are running correctly!"
    echo "   🚀 Ready to use the complete IP pipeline"
elif curl -s http://localhost:8000/v1/health >/dev/null 2>&1; then
    echo "   ⚠️  Backend running, but Streamlit is down"
    echo "   💡 Try: ./restart_services.sh"
elif curl -s http://localhost:8501 >/dev/null 2>&1; then
    echo "   ⚠️  Streamlit running, but backend is down"
    echo "   💡 Try: ./restart_services.sh"
else
    echo "   ❌ Both services are down"
    echo "   💡 Try: ./restart_services.sh"
fi

echo ""
echo "🛠️  Available commands:"
echo "   - Start services: ./restart_services.sh"
echo "   - Stop services:  ./stop_services.sh"
echo "   - Check status:   ./check_services.sh"
