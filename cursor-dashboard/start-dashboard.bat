@echo off
REM SportStatBot Cursor Dashboard Startup Script (Windows)
REM Starts both backend API and frontend development servers

echo.
echo Starting SportStatBot Cursor Dashboard...
echo.

REM Check if we're in the right directory
if not exist "package.json" (
    echo Error: Must run from cursor-dashboard directory
    echo Usage: cd cursor-dashboard ^&^& start-dashboard.bat
    pause
    exit /b 1
)

REM Kill any existing processes on our ports
echo Cleaning up existing processes...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":3000" ^| find "LISTENING"') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8000" ^| find "LISTENING"') do taskkill /F /PID %%a 2>nul

REM Start backend in new window
echo Starting backend API server (port 8000)...
start "SportStatBot API" cmd /k "cd backend && python api_server.py"

REM Wait for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend in new window
echo Starting frontend development server (port 3000)...
start "SportStatBot Dashboard" cmd /k "npm run dev"

REM Wait for frontend to start
timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo   Dashboard is ready!
echo ========================================
echo.
echo Frontend: http://localhost:3000
echo Backend API: http://localhost:8000
echo.
echo Close the server windows to stop
echo.
pause
