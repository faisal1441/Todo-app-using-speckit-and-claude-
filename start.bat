@echo off
REM Todo App Startup Script for Windows
REM Starts all three servers: Backend, Frontend, and Chat API

echo.
echo ========================================
echo   Todo App - Multi-Server Startup
echo ========================================
echo.

REM Check if Node is installed
where node >nul 2>nul
if errorlevel 1 (
    echo Error: Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

REM Check if Python is installed
where python >nul 2>nul
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

echo Node version:
node --version
echo Python version:
python --version
echo.

REM Ask user if they want to install dependencies
echo Checking if npm modules are installed...
if not exist "frontend\node_modules" (
    echo.
    echo Some dependencies are missing. Running: npm run install-all
    echo.
    call npm run install-all
    if errorlevel 1 (
        echo Error: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo   Starting All Servers...
echo ========================================
echo.
echo Backend Task API will run on:     http://localhost:8000/api
echo Chat API will run on:             http://localhost:3000
echo Frontend will run on:             http://localhost:5173
echo.
echo Press Ctrl+C to stop all servers
echo.

REM Run all servers
npm run dev

pause
