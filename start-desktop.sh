#!/bin/bash

# Script to start both backend and Electron desktop app

echo "🚀 Starting Market Dashboard Desktop App..."
echo ""

# Check if backend is running
if ! lsof -ti:5001 > /dev/null 2>&1; then
    echo "📡 Starting backend server..."
    cd backend
    python3 app.py &
    BACKEND_PID=$!
    cd ..
    sleep 3
    echo "✅ Backend server started (PID: $BACKEND_PID)"
else
    echo "✅ Backend server already running"
fi

# Start Electron app
echo "🖥️  Starting Electron desktop app..."
cd frontend
npm run electron:dev

# Cleanup on exit
trap "kill $BACKEND_PID 2>/dev/null" EXIT

