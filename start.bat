@echo off
REM Quick start for Windows
REM Tries python then python3

set PYTHON_CMD=
for %%P in (python python3) do (
    %%P --version >nul 2>&1
    if not defined PYTHON_CMD (
        if !errorlevel! equ 0 (
            set PYTHON_CMD=%%P
        )
    )
)

if not defined PYTHON_CMD (
    echo ERROR: Python not found
    exit /b 1
)

%PYTHON_CMD% start.py %*
