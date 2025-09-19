#!/bin/bash
# Start PayReady AI services

source .venv/bin/activate

# Start API server (if exists)
if [[ -f "api/main.py" ]]; then
    echo "Starting API server..."
    python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000 &
    API_PID=$!
    echo "API server PID: $API_PID"
fi

# Monitor logs
if [[ -d "logs" ]]; then
    echo "Monitoring logs..."
    tail -f logs/*.log 2>/dev/null &
    TAIL_PID=$!
fi

echo "Services started. Press Ctrl+C to stop."
wait
