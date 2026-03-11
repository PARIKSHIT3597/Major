@echo off
REM Script to start both backend and Electron desktop app on Windows

echo Starting Market Dashboard Desktop App...
echo.

REM Check if backend is running (Windows check)
netstat -an | findstr ":5001" >nul
if %errorlevel% neq 0 (
    echo Starting backend server...
    start /B python backend\app.py
    timeout /t 3 /nobreak >nul
    echo Backend server started
) else (
    echo Backend server already running
)

REM Start Electron app
echo Starting Electron desktop app...
cd frontend
call npm run electron:dev

