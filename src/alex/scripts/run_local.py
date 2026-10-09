#!/usr/bin/env python3
"""
Run both frontend and backend locally for development.
This script starts the NextJS frontend and FastAPI backend in parallel.
"""

import os
import sys
import subprocess
import signal
import time
from pathlib import Path

# On Windows, npm/node are .cmd files and need shell=True to be found
IS_WINDOWS = sys.platform == "win32"

# Track subprocesses for cleanup
processes = []

def stop_process(proc):
    """Stop a process and, on Windows, the children it spawned."""
    if proc.poll() is not None:
        return
    if IS_WINDOWS:
        subprocess.run(
            ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
            capture_output=True,
            text=True,
        )
        return
    try:
        proc.terminate()
        proc.wait(timeout=5)
    except Exception:
        proc.kill()


def cleanup(signum=None, frame=None):
    """Clean up all subprocess on exit"""
    print("\n🛑 Shutting down services...")
    for proc in processes:
        stop_process(proc)
    sys.exit(0)

# Register cleanup handlers
signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

def check_requirements():
    """Check if required tools are installed"""
    checks = []

    # Check Node.js
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        node_version = result.stdout.strip()
        checks.append(f"✅ Node.js: {node_version}")
    except FileNotFoundError:
        checks.append("❌ Node.js not found - please install Node.js")

    # Check npm
    try:
        result = subprocess.run(["npm", "--version"], capture_output=True, text=True, shell=IS_WINDOWS)
        npm_version = result.stdout.strip()
        checks.append(f"✅ npm: {npm_version}")
    except FileNotFoundError:
        checks.append("❌ npm not found - please install npm")

    # Check uv (which manages Python for us)
    try:
        result = subprocess.run(["uv", "--version"], capture_output=True, text=True)
        uv_version = result.stdout.strip()
        checks.append(f"✅ uv: {uv_version}")
    except FileNotFoundError:
        checks.append("❌ uv not found - please install uv")

    print("\n📋 Prerequisites Check:")
    for check in checks:
        print(f"  {check}")

    # Exit if any critical tools are missing
    if any("❌" in check for check in checks):
        print("\n⚠️  Please install missing dependencies and try again.")
        sys.exit(1)

def check_env_files():
    """Check if environment files exist"""
    project_root = Path(__file__).parent.parent

    root_env = project_root / ".env"
    frontend_env = project_root / "frontend" / ".env.local"

    missing = []

    if not root_env.exists():
        missing.append(".env (root project file)")
    if not frontend_env.exists():
        missing.append("frontend/.env.local")

    if missing:
        print("\n⚠️  Missing environment files:")
        for file in missing:
            print(f"  - {file}")
        print("\nPlease create these files with the required configuration.")
        print("The root .env should have all backend variables from Parts 1-7.")
        print("The frontend/.env.local should have Clerk keys.")
        sys.exit(1)

    print("✅ Environment files found")

def start_backend():
    """Start the FastAPI backend"""
    backend_dir = Path(__file__).parent.parent / "backend" / "api"

    print("\n🚀 Starting FastAPI backend...")

    # Check if dependencies are installed
    if not (backend_dir / ".venv").exists() and not (backend_dir / "uv.lock").exists():
        print("  Installing backend dependencies...")
        subprocess.run(["uv", "sync"], cwd=backend_dir, check=True)

    # Start the backend. Merge stderr so a bind failure is visible.
    proc = subprocess.Popen(
        ["uv", "run", "main.py"],
        cwd=backend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    processes.append(proc)

    # Wait until THIS process says it is listening. An HTTP check alone can
    # succeed against an older server that is already on port 8000.
    print("  Waiting for backend to start...")
    import threading
    ready = {"ok": False}

    def read_backend():
        for line in proc.stdout:
            print(f"    Backend: {line.strip()}")
            if "Uvicorn running" in line or "Application startup complete" in line:
                ready["ok"] = True

    threading.Thread(target=read_backend, daemon=True).start()

    for _ in range(30):  # 30 second timeout
        if proc.poll() is not None:
            print("  ❌ Backend exited during startup. Port 8000 is already in use if another API is still running.")
            cleanup()
        if ready["ok"]:
            print("  ✅ Backend running at http://localhost:8000")
            print("     API docs: http://localhost:8000/docs")
            return proc
        time.sleep(1)

    print("  ❌ Backend failed to start")
    cleanup()

def start_frontend():
    """Start the NextJS frontend"""
    frontend_dir = Path(__file__).parent.parent / "frontend"

    print("\n🚀 Starting NextJS frontend...")

    # Check if dependencies are installed
    if not (frontend_dir / "node_modules").exists():
        print("  Installing frontend dependencies...")
        subprocess.run(["npm", "install"], cwd=frontend_dir, check=True, shell=IS_WINDOWS)

    # Start the frontend
    proc = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=frontend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,  # Combine stderr with stdout
        text=True,
        bufsize=1,
        shell=IS_WINDOWS
    )
    processes.append(proc)

    # Wait until THIS process prints its own URL. Probing port 3000 accepts
    # a leftover Next.js server while the new one has moved to another port.
    print("  Waiting for frontend to start...")
    import threading

    started_flag = {"started": False, "blocked": False}

    def read_output():
        for line in proc.stdout:
            print(f"    Frontend: {line.strip()}")
            if "Port 3000 is in use" in line or "EPERM" in line:
                started_flag["blocked"] = True
            if "Local:" in line and "http://localhost:3000" in line:
                started_flag["started"] = True

    reader = threading.Thread(target=read_output, daemon=True)
    reader.start()

    for _ in range(30):  # 30 second timeout
        if proc.poll() is not None or started_flag["blocked"]:
            print("  ❌ Frontend could not use port 3000. Stop the other Next.js process and run this again.")
            cleanup()
        if started_flag["started"]:
            print("  ✅ Frontend running at http://localhost:3000")
            return proc
        time.sleep(1)

    print("  ❌ Frontend failed to start")
    cleanup()

def monitor_processes():
    """Monitor running processes and show their output"""
    print("\n" + "="*60)
    print("🎯 Alex Financial Advisor - Local Development")
    print("="*60)
    print("\n📍 Services:")
    print("  Frontend: http://localhost:3000")
    print("  Backend:  http://localhost:8000")
    print("  API Docs: http://localhost:8000/docs")
    print("\n📝 Logs will appear below. Press Ctrl+C to stop.\n")
    print("="*60 + "\n")

    # Reader threads already print each process's output.
    while True:
        for proc in processes:
            if proc.poll() is not None:
                print(f"\n⚠️  A process has stopped unexpectedly (exit {proc.returncode})!")
                cleanup()

        time.sleep(0.5)

def main():
    """Main entry point"""
    print("\n🔧 Alex Financial Advisor - Local Development Setup")
    print("="*50)

    # Check prerequisites
    check_requirements()
    check_env_files()

    # Install httpx if needed
    try:
        import httpx
    except ImportError:
        print("\n📦 Installing httpx for health checks...")
        subprocess.run(["uv", "add", "httpx"], check=True)

    # Start services
    backend_proc = start_backend()
    frontend_proc = start_frontend()

    # Monitor processes
    try:
        monitor_processes()
    except KeyboardInterrupt:
        cleanup()

if __name__ == "__main__":
    main()