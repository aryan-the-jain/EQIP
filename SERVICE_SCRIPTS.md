# Eqip.ai Service Management Scripts

These scripts help you easily manage the FastAPI backend and Streamlit frontend services.

## 🚀 Quick Start

```bash
# Start both services
./restart_services.sh

# Check if services are running
./check_services.sh

# Stop all services
./stop_services.sh
```

## 📋 Script Details

### `restart_services.sh`
**Purpose**: Kills existing processes and starts fresh backend + Streamlit services

**What it does**:
- Stops any running FastAPI and Streamlit processes
- Frees up ports 8000 and 8501
- Starts FastAPI backend on port 8000
- Starts enhanced Streamlit app on port 8501
- Waits for both services to be ready
- Saves process IDs for future management
- Creates log files in `logs/` directory

**Usage**:
```bash
./restart_services.sh
```

### `stop_services.sh`
**Purpose**: Gracefully stops all running services

**What it does**:
- Stops services using saved process IDs
- Kills any remaining FastAPI/Streamlit processes
- Force-kills processes if ports are still in use
- Verifies ports are freed up
- Cleans up PID files

**Usage**:
```bash
./stop_services.sh
```

### `check_services.sh`
**Purpose**: Provides detailed status information about all services

**What it shows**:
- Service health status (running/stopped)
- Process information and PIDs
- Port usage status
- Log file information with recent entries
- Overall system status
- Available commands

**Usage**:
```bash
./check_services.sh
```

## 🌐 Service URLs

When running:
- **FastAPI Backend**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Enhanced Streamlit**: http://localhost:8501

## 📝 Log Files

Logs are stored in the `logs/` directory:
- `logs/backend.log` - FastAPI backend logs
- `logs/streamlit.log` - Streamlit application logs

## 🔧 Troubleshooting

### Services won't start
1. Check if ports are in use: `./check_services.sh`
2. Force stop everything: `./stop_services.sh`
3. Try restarting: `./restart_services.sh`

### Port conflicts
If you get "port already in use" errors:
```bash
# Check what's using the ports
lsof -i :8000
lsof -i :8501

# Kill specific processes
kill -9 <PID>
```

### View recent logs
```bash
# Backend logs
tail -f logs/backend.log

# Streamlit logs  
tail -f logs/streamlit.log
```

## 🎯 Development Workflow

Typical development workflow:
1. `./restart_services.sh` - Start everything fresh
2. Make code changes
3. `./check_services.sh` - Verify services are running
4. Test your changes at http://localhost:8501
5. `./stop_services.sh` - Clean shutdown when done

The restart script is especially useful during development as it ensures a clean state every time you start working.
