#!/usr/bin/env python3
"""
Quick start script - starts both servers without full setup.
Assumes setup.py has already been run.
"""

import subprocess
import sys
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.absolute()
BACKEND_DIR = PROJECT_ROOT / "backend"
FRONTEND_DIR = PROJECT_ROOT / "frontend"

def main():
    print("=" * 50)
    print("    WAR GAME - Quick Start")
    print("=" * 50)
    print()

    # Determine Python path
    if os.name == 'nt':
        python_path = BACKEND_DIR / "venv" / "Scripts" / "python.exe"
    else:
        python_path = BACKEND_DIR / "venv" / "bin" / "python"

    if not python_path.exists():
        print("ERROR: Virtual environment not found!")
        print("Please run setup.py first:")
        print("  python setup.py")
        return 1

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
