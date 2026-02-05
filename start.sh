#!/bin/bash

# Todo App Startup Script for macOS/Linux
# Starts all three servers: Backend, Frontend, and Chat API

echo ""
echo "========================================"
echo "  Todo App - Multi-Server Startup"
echo "========================================"
echo ""

# Check if Node is installed
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed or not in PATH"
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    echo "Please install Python from https://www.python.org/"
    exit 1
fi

echo "Node version:"
node --version
echo "Python version:"
python3 --version
echo ""

# Check if dependencies are installed
echo "Checking if npm modules are installed..."
if [ ! -d "frontend/node_modules" ]; then
    echo ""
    echo "Some dependencies are missing. Running: npm run install-all"
    echo ""
    npm run install-all
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install dependencies"
        exit 1
    fi
fi

echo ""
echo "========================================"
echo "  Starting All Servers..."
echo "========================================"
echo ""
echo "Backend Task API will run on:     http://localhost:8000/api"
echo "Chat API will run on:             http://localhost:3000"
echo "Frontend will run on:             http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Run all servers
npm run dev
