@echo off
REM War Game Setup Script for Windows
REM This batch file provides a simple way to set up and run the game

echo.
echo ============================================
echo           WAR GAME SETUP
echo ============================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://python.org
    exit /b 1
)

REM Check if Node is available
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js 18+ from https://nodejs.org
    exit /b 1
)

REM Check if PostgreSQL is available
psql --version >nul 2>&1
if errorlevel 1 (
    echo WARNING: PostgreSQL is not in PATH
    echo Make sure PostgreSQL is running before continuing
    pause
)

REM Check if Redis is available
redis-cli --version >nul 2>&1
if errorlevel 1 (
    echo WARNING: Redis is not in PATH
    echo Make sure Redis is running before continuing
    pause
)

echo.
echo Running setup script...
echo.

REM Run the Python setup script
python setup.py %*

if errorlevel 1 (
    echo.
    echo Setup failed!
    pause
    exit /b 1
)

exit /b 0
