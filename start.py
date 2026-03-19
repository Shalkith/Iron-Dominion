#!/usr/bin/env python3
"""
Quick start script - starts both servers.
Creates venv if it doesn't exist (runs minimal setup).
"""

import subprocess
import sys
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.absolute()
BACKEND_DIR = PROJECT_ROOT / "backend"
FRONTEND_DIR = PROJECT_ROOT / "frontend"


def find_python():
    """Find the Python executable (python3 or python)."""
    for cmd in ["python3", "python"]:
        try:
            result = subprocess.run([cmd, "--version"], capture_output=True, text=True, check=False)
            if result.returncode == 0:
                return cmd
        except FileNotFoundError:
            continue
    return None


def run_command(cmd, cwd=None, check=True):
    """Run a shell command."""
    result = subprocess.run(
        cmd,
        cwd=cwd or PROJECT_ROOT,
        shell=isinstance(cmd, str),
        check=check,
        capture_output=True,
        text=True
    )
    return result


def create_venv(python_cmd):
    """Create virtual environment and install dependencies."""
    print("Creating virtual environment...")
    run_command([python_cmd, "-m", "venv", "venv"], cwd=BACKEND_DIR)

    # Determine python path in venv
    if os.name == 'nt':
        python_path = BACKEND_DIR / "venv" / "Scripts" / "python.exe"
    else:
        python_path = BACKEND_DIR / "venv" / "bin" / "python"

    print("Installing Python dependencies...")
    run_command([str(python_path), "-m", "pip", "install", "-r", "requirements.txt"], cwd=BACKEND_DIR)
    print("Done!")


def main():
    print("=" * 50)
    print("    WAR GAME - Quick Start")
    print("=" * 50)
    print()

    # Find system python
    python_cmd = find_python()
    if not python_cmd:
        print("ERROR: Python not found (tried 'python3' and 'python')")
        return 1

    # Determine venv python path
    if os.name == 'nt':
        python_path = BACKEND_DIR / "venv" / "Scripts" / "python.exe"
    else:
        python_path = BACKEND_DIR / "venv" / "bin" / "python"

    # Create venv if it doesn't exist
    if not python_path.exists():
        print("Virtual environment not found. Setting up...")
        print()
        try:
            create_venv(python_cmd)
        except Exception as e:
            print(f"ERROR: Failed to create venv: {e}")
            return 1
        print()

    # Check for node_modules
    if not (FRONTEND_DIR / "node_modules").exists():
        print("Installing frontend dependencies...")
        try:
            run_command(["npm", "install"], cwd=FRONTEND_DIR)
        except Exception as e:
            print(f"ERROR: Failed to install npm packages: {e}")
            return 1
        print()

    print("Starting servers...")
    print("  Backend:  http://localhost:8000")
    print("  Frontend: http://localhost:3000")
    print()
    print("Press Ctrl+C to stop")
    print()

    # Start backend
    backend_proc = subprocess.Popen(
        [str(python_path), "-m", "uvicorn", "app.main:app", "--reload", "--port", "8000"],
        cwd=BACKEND_DIR
    )

    # Start frontend
    frontend_proc = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=FRONTEND_DIR,
        shell=os.name == 'nt'
    )

    try:
        # Wait for both processes
        backend_proc.wait()
    except KeyboardInterrupt:
        print("\n\nStopping servers...")
        backend_proc.terminate()
        frontend_proc.terminate()
        print("Done!")

    return 0


if __name__ == "__main__":
    sys.exit(main())
