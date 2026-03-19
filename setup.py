#!/usr/bin/env python3
"""
War Game Setup Script

This script automates the entire setup process:
1. Checks prerequisites
2. Sets up the backend (venv, dependencies, database)
3. Sets up the frontend (npm install)
4. Seeds the database
5. Starts both servers

Usage:
    python setup.py
    python setup.py --skip-db  # Skip database initialization
    python setup.py --prod     # Production mode (no dev reload)
"""

import argparse
import os
import subprocess
import sys
import time
import shutil
from pathlib import Path

# Configuration
PROJECT_ROOT = Path(__file__).parent.absolute()
BACKEND_DIR = PROJECT_ROOT / "backend"
FRONTEND_DIR = PROJECT_ROOT / "frontend"
DATABASE_DIR = PROJECT_ROOT / "database"

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.END}\n")


def print_step(text):
    print(f"{Colors.BLUE}>>>{Colors.END} {text}")


def print_success(text):
    print(f"{Colors.GREEN}[OK]{Colors.END} {text}")


def print_error(text):
    print(f"{Colors.FAIL}[ERR]{Colors.END} {text}")


def print_warning(text):
    print(f"{Colors.WARNING}[!]{Colors.END} {text}")


def run_command(cmd, cwd=None, shell=False, check=True):
    """Run a shell command and return the result."""
    try:
        if shell and isinstance(cmd, list):
            cmd = ' '.join(cmd)

        result = subprocess.run(
            cmd,
            cwd=cwd or PROJECT_ROOT,
            shell=shell,
            check=check,
            capture_output=True,
            text=True
        )
        return result
    except subprocess.CalledProcessError as e:
        print_error(f"Command failed: {e}")
        if e.stdout:
            print(f"Stdout: {e.stdout}")
        if e.stderr:
            print(f"Stderr: {e.stderr}")
        raise


def check_prerequisites():
    """Check that all required tools are installed."""
    print_header("Checking Prerequisites")

    checks = [
        ("Python 3.9+", "python", ["--version"]),
        ("Node.js 18+", "node", ["--version"]),
        ("npm", "npm", ["--version"]),
        ("PostgreSQL", "psql", ["--version"]),
        ("Redis", "redis-cli", ["--version"]),
    ]

    all_good = True
    for name, cmd, args in checks:
        try:
            result = subprocess.run(
                [cmd] + args,
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                version = result.stdout.strip() or result.stderr.strip()
                print_success(f"{name}: {version}")
            else:
                print_error(f"{name}: Not found")
                all_good = False
        except FileNotFoundError:
            print_error(f"{name}: Not installed")
            all_good = False

    if not all_good:
        print("\nPlease install missing prerequisites:")
        print("  - Python: https://python.org")
        print("  - Node.js: https://nodejs.org")
        print("  - PostgreSQL: https://postgresql.org")
        print("  - Redis: https://redis.io")
        sys.exit(1)

    return True


def setup_backend(skip_db=False):
    """Set up the backend environment."""
    print_header("Setting Up Backend")

    # Create virtual environment
    venv_path = BACKEND_DIR / "venv"
    if venv_path.exists():
        print_warning("Virtual environment already exists, skipping creation")
    else:
        print_step("Creating Python virtual environment...")
        run_command([sys.executable, "-m", "venv", "venv"], cwd=BACKEND_DIR)
        print_success("Virtual environment created")

    # Determine pip path based on OS
    if os.name == 'nt':  # Windows
        pip_path = venv_path / "Scripts" / "pip.exe"
        python_path = venv_path / "Scripts" / "python.exe"
    else:  # Unix/Mac
        pip_path = venv_path / "bin" / "pip"
        python_path = venv_path / "bin" / "python"

    # Install dependencies
    print_step("Installing Python dependencies...")
    run_command([str(pip_path), "install", "-r", "requirements.txt"], cwd=BACKEND_DIR)
    print_success("Dependencies installed")

    # Create .env file if it doesn't exist
    env_file = BACKEND_DIR / ".env"
    env_example = BACKEND_DIR / ".env.example"
    if not env_file.exists() and env_example.exists():
        print_step("Creating .env file from template...")
        shutil.copy(env_example, env_file)
        print_warning("Please review the .env file and update database credentials if needed")
        print(f"  Location: {env_file}")

    if skip_db:
        print_warning("Skipping database initialization")
        return python_path

    # Initialize database
    print_step("Initializing database...")
    try:
        # Try to create database if it doesn't exist
        result = subprocess.run(
            ["createdb", "wargame"],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0:
            print_success("Database 'wargame' created")
        else:
            if "already exists" in result.stderr.lower():
                print_warning("Database 'wargame' already exists")
            else:
                print_error(f"Could not create database: {result.stderr}")
                print("Please create the database manually:")
                print("  createdb wargame")
    except FileNotFoundError:
        print_warning("createdb command not found, skipping database creation")
        print("Please ensure the database exists manually")

    # Initialize tables
    print_step("Creating database tables...")
    init_script = """
import asyncio
import sys
sys.path.insert(0, str(""" + f'"{BACKEND_DIR}"' + """))
from app.database import init_db
asyncio.run(init_db())
print("Database initialized successfully!")
"""
    run_command([str(python_path), "-c", init_script], cwd=BACKEND_DIR)
    print_success("Database tables created")

    # Seed the map
    print_step("Generating game map...")
    seed_script = """
import asyncio
import sys
sys.path.insert(0, str(""" + f'"{BACKEND_DIR}"' + """))
from app.database import init_db, AsyncSessionLocal
from app.services.tile_service import TileService

async def seed():
    await init_db()
    async with AsyncSessionLocal() as db:
        from sqlalchemy import select, func
        from app.models.tile import Tile
        result = await db.execute(select(func.count()).select_from(Tile))
        count = result.scalar()
        if count > 0:
            print(f"Map already exists with {count} tiles. Skipping.")
            return

        import random
        tiles = []
        for x in range(50):
            for y in range(50):
                tile = Tile(x=x, y=y, resource_value=random.randint(1, 5))
                db.add(tile)
                tiles.append(tile)
        await db.commit()
        print(f"Generated {len(tiles)} tiles successfully!")

asyncio.run(seed())
"""
    run_command([str(python_path), "-c", seed_script], cwd=BACKEND_DIR)
    print_success("Game map generated")

    return python_path


def setup_frontend():
    """Set up the frontend environment."""
    print_header("Setting Up Frontend")

    # Check if node_modules exists
    node_modules = FRONTEND_DIR / "node_modules"
    if node_modules.exists():
        print_warning("node_modules already exists, skipping npm install")
    else:
        print_step("Installing npm dependencies...")
        run_command(["npm", "install"], cwd=FRONTEND_DIR)
        print_success("Frontend dependencies installed")


def start_servers(python_path, prod=False):
    """Start the backend and frontend servers."""
    print_header("Starting Servers")

    processes = []

    # Start backend
    print_step("Starting backend server...")
    backend_cmd = [str(python_path), "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
    if not prod:
        backend_cmd.extend(["--reload"])

    backend_proc = subprocess.Popen(
        backend_cmd,
        cwd=BACKEND_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True
    )
    processes.append(("Backend", backend_proc))
    print_success(f"Backend started on http://localhost:8000")
    if not prod:
        print(f"  API docs: http://localhost:8000/docs")

    # Wait a moment for backend to start
    time.sleep(2)

    # Start frontend
    print_step("Starting frontend server...")
    frontend_proc = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=FRONTEND_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True,
        shell=os.name == 'nt'
    )
    processes.append(("Frontend", frontend_proc))
    print_success(f"Frontend started on http://localhost:3000")

    print_header("Servers Running")
    print(f"{Colors.GREEN}Backend:{Colors.END}  http://localhost:8000")
    print(f"{Colors.GREEN}Frontend:{Colors.END} http://localhost:3000")
    print(f"\n{Colors.WARNING}Press Ctrl+C to stop all servers{Colors.END}\n")

    # Stream output from both processes
    try:
        import select
        import fcntl
        import os

        # Set non-blocking mode for Unix
        if os.name != 'nt':
            for name, proc in processes:
                fd = proc.stdout.fileno()
                fl = fcntl.fcntl(fd, fcntl.F_GETFL)
                fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

        while True:
            for name, proc in processes:
                try:
                    if os.name == 'nt':
                        # Windows - blocking read with timeout
                        import msvcrt
                        if msvcrt.kbhit():
                            raise KeyboardInterrupt
                    else:
                        # Unix - non-blocking read
                        ready, _, _ = select.select([proc.stdout], [], [], 0.1)
                        if ready:
                            line = proc.stdout.readline()
                            if line:
                                print(f"[{Colors.CYAN}{name}{Colors.END}] {line.rstrip()}")
                except (IOError, OSError):
                    pass
                except KeyboardInterrupt:
                    raise

                # Check if process died
                if proc.poll() is not None:
                    print_error(f"{name} server stopped unexpectedly!")
                    return

    except KeyboardInterrupt:
        print("\n")
        print_header("Shutting Down Servers")
        for name, proc in processes:
            print_step(f"Stopping {name}...")
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
        print_success("All servers stopped")


def main():
    parser = argparse.ArgumentParser(description="War Game Setup Script")
    parser.add_argument("--skip-db", action="store_true", help="Skip database initialization")
    parser.add_argument("--skip-checks", action="store_true", help="Skip prerequisite checks")
    parser.add_argument("--prod", action="store_true", help="Production mode (no reload)")
    parser.add_argument("--setup-only", action="store_true", help="Only setup, don't start servers")
    args = parser.parse_args()

    try:
        # Print banner
        print(f"""
{Colors.CYAN}
==============================================================

                    WAR GAME SETUP

        Multiplayer Strategy Game - MVP Edition

==============================================================
{Colors.END}
""")

        # Check prerequisites
        if not args.skip_checks:
            check_prerequisites()
        else:
            print_warning("Skipping prerequisite checks")

        # Setup backend
        python_path = setup_backend(skip_db=args.skip_db)

        # Setup frontend
        setup_frontend()

        if args.setup_only:
            print_header("Setup Complete")
            print("Run the following commands to start the servers:")
            print(f"\n  Backend:")
            print(f"    cd backend")
            print(f"    {python_path} -m uvicorn app.main:app --reload")
            print(f"\n  Frontend:")
            print(f"    cd frontend")
            print(f"    npm run dev")
            return

        # Start servers
        start_servers(python_path, prod=args.prod)

    except Exception as e:
        print_error(f"Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
